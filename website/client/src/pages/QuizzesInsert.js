import React, { useState, useEffect } from "react";
import api from "../../../api";
import styled from "styled-components";

const Title = styled.h1.attrs({
  className: "h1",
})``;

const Wrapper = styled.div.attrs({
  className: "form-group",
})`
  margin: 0 30px;
`;

const Label = styled.label`
  margin: 5px;
`;

const InputText = styled.input.attrs({
  className: "form-control",
})`
  margin: 5px;
`;

const Button = styled.button.attrs({
  className: `btn btn-primary`,
})`
  margin: 15px 15px 15px 5px;
`;

const CancelButton = styled.a.attrs({
  className: `btn btn-danger`,
})`
  margin: 15px 15px 15px 5px;
`;

const QuizzesInsert = (props) => {
  const [name, setName] = useState("");
  const [questions, setQuestions] = useState("");

  const handleChangeInputName = async (event) => {
    const name = event.target.value;
    setName(name);
  };

  const handleChangeInputQuestions = async (event) => {
    const questions = event.target.value;
    setQuestions(questions);
  };

  const handleIncludeQuiz = async () => {
    const arrayQuestions = questions.split("/");
    const payload = { name, questions: arrayQuestions };

    await api.insertQuiz(payload).then((res) => {
      window.alert(`Movie inserted successfully`);
      setName("");
      setQuestions("");
    });
  };

  return (
    <Wrapper>
      <Title>Create Quiz</Title>

      <Label>Name: </Label>
      <InputText
        type="text"
        value={name}
        onChange={handleChangeInputName}
      />

      <Label>Questions: </Label>
      <InputText
        type="text"
        value={questions}
        onChange={handleChangeInputQuestions}
      />

      <Button onClick={handleIncludeQuiz}>Add Quiz</Button>
      <CancelButton href={"/quizzes/list"}>Cancel</CancelButton>
    </Wrapper>
  );
};

export default QuizzesInsert;
