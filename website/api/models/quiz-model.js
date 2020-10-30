const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const Quiz = new Schema(
  {
    name: { type: String, required: true },
    questions: { type: [String], required: true },
  },
  { timestamps: true }
);

module.exports = mongoose.model("quizInfo", Quiz);
