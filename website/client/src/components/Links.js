import React from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";

const Collapse = styled.div.attrs({
  className: "collpase navbar-collapse",
})``;

const List = styled.div.attrs({
  className: "navbar-nav mr-auto",
})``;

const Item = styled.div.attrs({
  className: "collpase navbar-collapse",
})``;

const Links = (props) => {
  return (
    <React.Fragment>
      <Link to="/" className="navbar-brand">
        QuizBot
      </Link>
      <Collapse>
        <List>
          <Item>
            <Link to="/quizzes/list" className="nav-link">
              List Quizzes
            </Link>
          </Item>
          <Item>
            <Link to="/quizzes/create" className="nav-link">
              Create Quiz
            </Link>
          </Item>
        </List>
      </Collapse>
    </React.Fragment>
  );
};

export default Links;
