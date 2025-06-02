error id: file://<WORKSPACE>/ModelServer/src/main/scala/ModelServer.scala:`<none>`.
file://<WORKSPACE>/ModelServer/src/main/scala/ModelServer.scala
empty definition using pc, found symbol in pc: `<none>`.
empty definition using semanticdb
empty definition using fallback
non-local guesses:
	 -akka/http/scaladsl/model/jsonFormat1.
	 -akka/http/scaladsl/model/jsonFormat1#
	 -akka/http/scaladsl/model/jsonFormat1().
	 -spray/json/jsonFormat1.
	 -spray/json/jsonFormat1#
	 -spray/json/jsonFormat1().
	 -scala/concurrent/duration/jsonFormat1.
	 -scala/concurrent/duration/jsonFormat1#
	 -scala/concurrent/duration/jsonFormat1().
	 -akka/http/scaladsl/server/Directives.jsonFormat1.
	 -akka/http/scaladsl/server/Directives.jsonFormat1#
	 -akka/http/scaladsl/server/Directives.jsonFormat1().
	 -akka/http/scaladsl/marshallers/sprayjson/SprayJsonSupport.jsonFormat1.
	 -akka/http/scaladsl/marshallers/sprayjson/SprayJsonSupport.jsonFormat1#
	 -akka/http/scaladsl/marshallers/sprayjson/SprayJsonSupport.jsonFormat1().
	 -spray/json/DefaultJsonProtocol.jsonFormat1.
	 -spray/json/DefaultJsonProtocol.jsonFormat1#
	 -spray/json/DefaultJsonProtocol.jsonFormat1().
	 -org/mongodb/scala/jsonFormat1.
	 -org/mongodb/scala/jsonFormat1#
	 -org/mongodb/scala/jsonFormat1().
	 -org/mongodb/scala/model/Filters.jsonFormat1.
	 -org/mongodb/scala/model/Filters.jsonFormat1#
	 -org/mongodb/scala/model/Filters.jsonFormat1().
	 -scala/collection/JavaConverters.jsonFormat1.
	 -scala/collection/JavaConverters.jsonFormat1#
	 -scala/collection/JavaConverters.jsonFormat1().
	 -scala/jdk/CollectionConverters.jsonFormat1.
	 -scala/jdk/CollectionConverters.jsonFormat1#
	 -scala/jdk/CollectionConverters.jsonFormat1().
	 -jsonFormat1.
	 -jsonFormat1#
	 -jsonFormat1().
	 -scala/Predef.jsonFormat1.
	 -scala/Predef.jsonFormat1#
	 -scala/Predef.jsonFormat1().
offset: 1356
uri: file://<WORKSPACE>/ModelServer/src/main/scala/ModelServer.scala
text:
```scala
import akka.actor.ActorSystem
import akka.http.scaladsl.Http
import akka.http.scaladsl.model._
import akka.http.scaladsl.unmarshalling.Unmarshal
import akka.stream.ActorMaterializer
import spray.json._
import scala.concurrent.duration._
import scala.util.{Success, Failure}
import akka.http.scaladsl.server.Directives._
import akka.http.scaladsl.server.Route
import akka.http.scaladsl.model.headers.`Access-Control-Allow-Origin`
import akka.http.scaladsl.marshallers.sprayjson.SprayJsonSupport._
import spray.json.DefaultJsonProtocol._
import org.mongodb.scala._
import org.mongodb.scala.bson.{BsonValue, BsonDouble, BsonArray, ObjectId}
import org.mongodb.scala.model.Filters._
import scala.concurrent.Future
import scala.collection.JavaConverters._
import scala.jdk.CollectionConverters._

// --- Case classes ---
case class Input(gender: Double, age: Double, height: Double, weight: Double, duration: Double, heartRate: Double, bodyTemp: Double)
case class PythonRequest(features: Array[Double])
case class PythonResponse(status: String, prediction: Double)
case class PredictionRecord(_id: ObjectId, userId: String, timestamp: Long, input: Input, prediction: Double)

// --- JSON formats ---
object JsonFormats {
  implicit val inputFormat: RootJsonFormat[Input] = jsonFormat7(Input)
  implicit val pythonRequestFormat: RootJsonFormat[PythonRequest] = @@jsonFormat1(PythonRequest)
  implicit val pythonResponseFormat: RootJsonFormat[PythonResponse] = jsonFormat2(PythonResponse)
  implicit val predictionRecordFormat: RootJsonFormat[PredictionRecord] = jsonFormat5(PredictionRecord)
  implicit object ObjectIdJsonFormat extends RootJsonFormat[ObjectId] {
  def write(objId: ObjectId): JsValue = JsString(objId.toHexString)
  def read(json: JsValue): ObjectId = json match {
    case JsString(hexStr) => new ObjectId(hexStr)
    case _ => deserializationError("Expected hexadecimal ObjectId string")
  }
}

}

object ModelServer extends App {
  import JsonFormats._
  import scala.concurrent.ExecutionContext.Implicits.global

  implicit val system = ActorSystem("model-api")
  implicit val materializer = ActorMaterializer()

  val pythonModelUrl = "http://localhost:5000/predict"

  // --- CORS headers ---
  val corsHeaders = List(
    `Access-Control-Allow-Origin`.*,
    headers.RawHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS"),
    headers.RawHeader("Access-Control-Allow-Headers", "Content-Type")
  )

  // --- MongoDB setup ---
  val mongoClient: MongoClient = MongoClient()
  val database: MongoDatabase = mongoClient.getDatabase("calories_prediction")
  val collection: MongoCollection[Document] = database.getCollection("predictions")

  // --- Convert BSON array to Input ---
  def documentToInput(doc: Document): Input = {
    val features = doc.get("features").get.asArray().getValues.asScala.map(_.asDouble().getValue)
    Input(
      features(0),
      features(1),
      features(2),
      features(3),
      features(4),
      features(5),
      features(6)
    )
  }

  // --- Route definition ---
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

  // --- Start server ---
  val bindingFuture = Http().bindAndHandle(route, "localhost", 8080)
  println("Server online at http://localhost:8080/\nPress ENTER to stop...")
  scala.io.StdIn.readLine()

  // --- Shutdown hook ---
  scala.sys.addShutdownHook {
    mongoClient.close()
    system.terminate()
  }
}

```


#### Short summary: 

empty definition using pc, found symbol in pc: `<none>`.