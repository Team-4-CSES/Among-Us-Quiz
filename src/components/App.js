import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { NavBar } from "../components";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import {
  QuizzesList,
  QuizzesInsert,
  QuizzesUpdate,
  MainContent,
} from "../pages";

const App = (props) => {
  return (
    <Router>
      <NavBar />
      <Switch>
        <Route path="/" exact component={MainContent} />
        <Route path="/quizzes/list" exact component={QuizzesList} />
        <Route path="/quizzes/create" exact component={QuizzesInsert} />
        <Route path="/quizzes/update/:id" exact component={QuizzesUpdate} />
      </Switch>
    </Router>
  );
};

export default App;
