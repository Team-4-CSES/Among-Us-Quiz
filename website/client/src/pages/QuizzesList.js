import React, { useState, useEffect } from "react";
import ReactTable from "react-table-6";
import api from "../../../api";

import styled from "styled-components";

import "react-table-6/react-table.css";
import { QuizzesUpdate } from ".";

const Wrapper = styled.div`
  padding: 0 40px 40px 40px;
`;

const Update = styled.div`
  color: #ef9b0f;
  cursor: pointer;
`;

const Delete = styled.div`
  color: #ff0000;
  cursor: pointer;
`;

const UpdateQuiz = (props) => {
  const updateUser = (event) => {
    event.preventDefault();
    window.location.href = `/quizzes/update/${props.id}`;
  };

  return <Update onClick={updateUser}>Update</Update>;
};

const DeleteQuiz = (props) => {
  const deleteUser = (event) => {
    event.preventDefault();
    if (
      window.confirm(`Do you want to delete the quiz ${props.id} permanently?`)
    ) {
      api.deleteQuizById(props.id);
      window.location.reload();
    }
  };

  return <Delete onClick={deleteUser}>Delete</Delete>;
};

const QuizzesList = (props) => {
  const [quizzes, setQuizzes] = useState([]);
  const [columns, setColumns] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    const fetchData = async () => {
      await api.getAllQuizzes().then((quizzes) => {
        if (mounted) {
          setQuizzes(quizzes.data.data);
          setIsLoading(false);
        }
      });
    };
    fetchData();

    return () => (mounted = false);
  }, []);

  setTimeout(() => {
    setColumns([
      {
        Header: "ID",
        accessor: "_id",
        filterable: true,
      },
      {
        Header: "Name",
        accessor: "name",
        filterable: true,
      },
      {
        Header: "Questions",
        accessor: "questions",
        Cell: (props) => <span>{props.value.join(" / ")}</span>,
      },
      {
        Header: "",
        accessor: "",
        Cell: function (props) {
          return (
            <span>
              <DeleteQuiz id={props.original._id} />
            </span>
          );
        },
      },
      {
        Header: "",
        accessor: "",
        Cell: function (props) {
          return (
            <span>
              <UpdateQuiz id={props.original._id} />
            </span>
          );
        },
      },
    ]);
  }, 1000);

  let showTable = true;
  if (!quizzes.length) {
    showTable = false;
  }

  return (
    <Wrapper>
      {showTable && (
        <ReactTable
          data={quizzes}
          columns={columns}
          loading={isLoading}
          defaultPageSize={10}
          showPageSizeOptions={true}
          minRows={0}
        />
      )}
    </Wrapper>
  );
};

export default QuizzesList;
