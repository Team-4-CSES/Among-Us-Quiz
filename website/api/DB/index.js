const mongoose = require("mongoose");

const uri = "mongodb+srv://eric:supepcoo101@cluster0.tes7n.mongodb.net/quizInfo?retryWrites=true&w=majority";
mongoose
  .connect(uri, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .catch((e) => {
    console.error("Connection error", e.message);
  });

const db = mongoose.connection;

module.exports = db;
