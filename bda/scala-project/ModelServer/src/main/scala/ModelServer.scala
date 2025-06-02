import akka.actor.ActorSystem
import akka.http.scaladsl.Http
import akka.http.scaladsl.model._
import akka.http.scaladsl.unmarshalling.Unmarshal
import akka.stream.ActorMaterializer
import akka.http.scaladsl.server.Directives._
import akka.http.scaladsl.server.Route
import akka.http.scaladsl.model.headers.`Access-Control-Allow-Origin`
import akka.http.scaladsl.marshallers.sprayjson.SprayJsonSupport._
import org.mongodb.scala._
import org.mongodb.scala.bson.{BsonDouble, BsonArray, ObjectId}
import org.mongodb.scala.model.Filters._
import scala.concurrent.Future
import scala.collection.JavaConverters._
import scala.concurrent.ExecutionContext.Implicits.global
import spray.json._
import MongoJsonFormats._

object ModelServer extends App {
  implicit val system = ActorSystem("model-api")
  implicit val materializer = ActorMaterializer()

  val pythonModelUrl = "http://localhost:5000/predict"

  val corsHeaders = List(
    `Access-Control-Allow-Origin`.*,
    headers.RawHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS"),
    headers.RawHeader("Access-Control-Allow-Headers", "Content-Type")
  )

  val mongoClient: MongoClient = MongoClient()
  val database: MongoDatabase = mongoClient.getDatabase("calories_prediction")
  val collection: MongoCollection[Document] = database.getCollection("predictions")

  def documentToInput(doc: Document): Input = {
    val features = doc.get("features").get.asArray().getValues.asScala.toList.map(_.asDouble().getValue)
    Input(features(0), features(1), features(2), features(3), features(4), features(5), features(6))
  }

  val route: Route =
    (path("predict") & post) {
      entity(as[PythonRequest]) { request =>
        parameter('userId) { userId =>
          complete {
            val predictionFuture = Http().singleRequest(
              HttpRequest(
                method = HttpMethods.POST,
                uri = pythonModelUrl,
                entity = HttpEntity(ContentTypes.`application/json`, request.toJson.compactPrint)
              )
            ).flatMap { response =>
              Unmarshal(response.entity).to[String].flatMap { body =>
                val predictionValue = body.parseJson.convertTo[PythonResponse].prediction

                val features = request.features.map(BsonDouble(_))
                val bsonArray = BsonArray.fromIterable(features.toIterable)

                val doc = Document(
                  "_id" -> new ObjectId(),
                  "userId" -> userId,
                  "timestamp" -> System.currentTimeMillis(),
                  "features" -> bsonArray,
                  "prediction" -> BsonDouble(predictionValue)
                )

                collection.insertOne(doc).toFuture().map { _ =>
                  HttpResponse(
                    status = StatusCodes.OK,
                    entity = HttpEntity(ContentTypes.`application/json`, body),
                    headers = corsHeaders
                  )
                }
              }
            }
            predictionFuture
          }
        }
      }
    } ~
    (path("history") & get) {
      parameter('userId) { userId =>
        complete {
          collection.find(equal("userId", userId))
            .sort(Document("timestamp" -> -1))
            .limit(5)
            .toFuture()
            .map { docs =>
              val records = docs.map { doc =>
                val input = documentToInput(doc)
                PredictionRecord(
                  doc.getObjectId("_id"),
                  doc.getString("userId"),
                  doc.getLong("timestamp"),
                  input,
                  doc.getDouble("prediction")
                )
              }
              HttpResponse(
                status = StatusCodes.OK,
                entity = HttpEntity(ContentTypes.`application/json`, records.toJson.compactPrint),
                headers = corsHeaders
              )
            }
        }
      }
    } ~
    options {
      complete(HttpResponse(
        status = StatusCodes.OK,
        headers = corsHeaders
      ))
    }

  val bindingFuture = Http().bindAndHandle(route, "localhost", 8080)
  println("Server online at http://localhost:8080/\nPress ENTER to stop...")
  scala.io.StdIn.readLine()

  scala.sys.addShutdownHook {
    mongoClient.close()
    system.terminate()
  }
}
