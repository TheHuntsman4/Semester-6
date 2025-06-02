name := "ModelServer"

version := "0.1"

scalaVersion := "2.12.17"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % "3.4.1",
  "org.apache.spark" %% "spark-sql" % "3.4.1",
  "org.apache.spark" %% "spark-mllib" % "3.4.1",

  "com.typesafe.akka" %% "akka-actor" % "2.6.20",
  "com.typesafe.akka" %% "akka-stream" % "2.6.20",
  "com.typesafe.akka" %% "akka-http" % "10.2.10",
  "com.typesafe.akka" %% "akka-http-spray-json" % "10.2.10",  

  "io.spray" %% "spray-json" % "1.3.6",
  "org.mongodb.scala" %% "mongo-scala-driver" % "4.9.0"
)

dependencyOverrides += "org.scala-lang.modules" %% "scala-parser-combinators" % "2.1.1"