import React, { useState, useEffect } from "react";
// import "../style/App.css";
import NavBar from "./NavBar.js";
import MainContent from "./MainContent";

const App = (props) => {
  const [apiResponse, setApiResponse] = useState("");

  const callAPI = () => {
    fetch("http://localhost:9000/testAPI")
      .then((res) => res.text())
      .then((res) => setApiResponse(res));
  };

  useEffect(() => {
    callAPI();
  }, []);

  return (
    <div className="App">
      <p className = "App-intro">{apiResponse}</p>
      <NavBar />
      <MainContent />
    </div>
  );
};

export default App;
