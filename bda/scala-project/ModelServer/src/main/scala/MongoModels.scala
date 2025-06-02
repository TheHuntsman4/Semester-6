import org.mongodb.scala.bson.ObjectId
import spray.json._
import DefaultJsonProtocol._

// Case classes
case class Input(gender: Double, age: Double, height: Double, weight: Double, duration: Double, heartRate: Double, bodyTemp: Double)
case class PythonRequest(features: Array[Double])
case class PythonResponse(status: String, prediction: Double)
case class PredictionRecord(_id: ObjectId, userId: String, timestamp: Long, input: Input, prediction: Double)

// JSON formats
object MongoJsonFormats extends DefaultJsonProtocol {
  implicit object ObjectIdJsonFormat extends RootJsonFormat[ObjectId] {
    def write(objId: ObjectId): JsValue = JsString(objId.toHexString)
    def read(json: JsValue): ObjectId = json match {
      case JsString(hexStr) => new ObjectId(hexStr)
      case _ => deserializationError("Expected hexadecimal ObjectId string")
    }
  }

  implicit val inputFormat: RootJsonFormat[Input] = jsonFormat7(Input)
  implicit val pythonRequestFormat: RootJsonFormat[PythonRequest] = jsonFormat1(PythonRequest)
  implicit val pythonResponseFormat: RootJsonFormat[PythonResponse] = jsonFormat2(PythonResponse)
  implicit val predictionRecordFormat: RootJsonFormat[PredictionRecord] = jsonFormat5(PredictionRecord)
}
