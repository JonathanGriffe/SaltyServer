import React from "react";
import ReactDOM from "react-dom";
import "./index.css";

var ws_url = "ws://localhost:8000/ws/status/";
var ticksSocket = new WebSocket(ws_url);

class Data extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      red: {
        name: null,
        wins: 0,
        losses: 0,
        avgBetShare: 0,
      },
      blue: {
        name: null,
        wins: 0,
        losses: 0,
        avgBetShare: 0,
      },
      status: null,
      NScoreDiff: 0,
    };
  }

  setStatus(data) {
    this.setState(data);
  }

  componentDidMount() {
    ticksSocket.onmessage = function (event) {
      var data = JSON.parse(event.data);
      console.log(data);
      this.setState(data);
    }.bind(this);
  }

  render() {
    var status = null;
    switch (this.state.status) {
      case "1":
        status = this.state.red.name + " won !";
        break;
      case "2":
        status = this.state.blue.name + " won !";
        break;
      case "open":
        status = "Bets are open !";
        break;
      case "locked":
        status = "Bets are closed !";
        break;
    }
    var prediction = null;
    if (this.state.NScoreDiff >= 0.15 && this.state.NScoreDiff < 0.3) {
      prediction = (
        <h2>
          <span className="red">{this.state.red.name}</span> is more likely to
          win <span className="green">(+{this.state.NScoreDiff})</span>
        </h2>
      );
    } else if (this.state.NScoreDiff >= 0.3 && this.state.NScoreDiff < 0.45) {
      prediction = (
        <h2>
          <span className="red">{this.state.red.name}</span> is predicted to win{" "}
          <span className="green">(+{this.state.NScoreDiff})</span>
        </h2>
      );
    } else if (this.state.NScoreDiff >= 0.45) {
      prediction = (
        <h2>
          <span className="red">{this.state.red.name}</span> will probably win{" "}
          <span className="green">(+{this.state.NScoreDiff})</span>
        </h2>
      );
    } else if (this.state.NScoreDiff <= -0.15 && this.state.NScoreDiff > -0.3) {
      prediction = (
        <h2>
          <span className="blue">{this.state.blue.name}</span> is more likely to
          win <span className="green">(+{-this.state.NScoreDiff})</span>
        </h2>
      );
    } else if (this.state.NScoreDiff <= -0.3 && this.state.NScoreDiff > -0.45) {
      prediction = (
        <h2>
          <span className="blue">{this.state.blue.name}</span> is predicted to
          win <span className="green">(+{-this.state.NScoreDiff})</span>
        </h2>
      );
    } else if (this.state.NScoreDiff <= -0.45) {
      prediction = (
        <h2>
          <span className="blue">{this.state.blue.name}</span> is predicted to
          win <span className="green">(+{-this.state.NScoreDiff})</span>
        </h2>
      );
    } else {
      prediction = (
        <h2>
          Cannot make a prediction ({this.state.NScoreDiff >= 0 ? "+" : ""}
          {this.state.NScoreDiff})
        </h2>
      );
    }
    console.log(status);
    return (
      <div className="board">
        <h2>
          <span className="red">{this.state.red.name}</span> vs{" "}
          <span className="blue">{this.state.blue.name}</span>
        </h2>
        <br></br>
        <h2>{status}</h2>
        <br></br>
        {prediction}
      </div>
    );
  }
}

ReactDOM.render(<Data />, document.getElementById("root"));
