import React from "react";
// import "../style/App.css";
import NavBar from "./NavBar.js"
import MainContent from "./MainContent"

const App = (props) => {
  return (
    <div className="App">
      <NavBar />
      <MainContent />
    </div>
  );
};

export default App;