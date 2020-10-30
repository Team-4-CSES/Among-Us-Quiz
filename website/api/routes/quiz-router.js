const express = require("express");

const QuizCtrl = require("../controllers/quiz-ctrl");

const router = express.Router();

router.post("/quiz", QuizCtrl.createQuiz);
router.put("/quiz/:id", QuizCtrl.updateQuiz);
router.delete("/quiz/:id", QuizCtrl.deleteQuiz);
router.get("/quiz/:id", QuizCtrl.getQuizById);
router.get("/quizzes", QuizCtrl.getQuizzes);

module.exports = router;
