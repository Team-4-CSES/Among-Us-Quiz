import React from "react";
import "../style/mainContent.css";

const MainContent = (props) => {
  return (
    <div className="mainContent">
      <h1>Team 4 Quiz Bot</h1>
      <a href = "https://discord.com/oauth2/authorize?client_id=765746012282683393&scope=bot&permissions=355392">Invite the Bot!</a>
      <h2>
        This bot allows multiple user to participate in a contest in which they
        answer multiple choice questions uploaded by a user onto a server. There
        are two ways in which the quiz is played.
      </h2>
      <h3>Points</h3>
      <p>
        Players get points based on the correctness of their answers, as well as
        the speed at which they answered. The winner is the player with the most
        points.
      </p>
      <h3>Knock-out</h3>
      <p>
        Players in a voice channel can start a quiz with the people in the voice
        channel, and people get kicked out of the channel if they get a question
        wrong. The last player left in the voice channel wins!
      </p>
      <h3>Using the bot</h3>
      <p>
        Add the bot to your server and choose from any of the available quizzes
        in the database to play!
      </p>
    </div>
  );
};

export default MainContent;
