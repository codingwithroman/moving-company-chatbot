"use client";
import { useState } from "react";
import Chatbot from "react-chatbot-kit";
import "react-chatbot-kit/build/main.css";
import { createChatBotMessage } from "react-chatbot-kit";
import "react-chatbot-kit/build/main.css";
import "./chatbot-styles.css";
import PredefinedOptions from "./pages/PredefinedOptions.js"


const botAvatar = 'robot-assistant.png';

// greeting based on the current time
const getTimeBasedGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12 && hour > 4) {
    return "Goedemorgen"; 
  } else if (hour < 18) {
    return "Goedemiddag"; 
  } else {
    return "Goedenavond"; 
  }
};

// Configuration for the chatbot
const config = {
  initialMessages: [
    createChatBotMessage(`${getTimeBasedGreeting()}! Hoe kan ik je vandaag helpen?`),
  ],
  botName: "MoveBot",
  customComponents: {
    botAvatar: (props) => 
      <div className="custom-bot-avatar-container">
        <img 
          src={botAvatar} 
          alt="Bot Avatar" 
          className="custom-bot-avatar" 
          {...props}
        />
      </div>
  },
  widgets: [
    {
      widgetName: "options",
      widgetFunc: (props) => <PredefinedOptions {...props} />,
    }
  ]
};

// MessageParser class
class MessageParser {
  constructor(actionProvider, state) {
    this.actionProvider = actionProvider;
    this.state = state;
  }

  parse(message) {
    this.actionProvider.handleMessage(message);
  }
}

// ActionProvider class
class ActionProvider {
  constructor(createChatBotMessage, setStateFunc, createClientMessage) {
    this.createChatBotMessage = createChatBotMessage;
    this.setState = setStateFunc;
    this.createClientMessage = createClientMessage;
  }

  async handleMessage(message) {
    try {
      const response = await fetch("http://localhost:5000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: message }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error("Server error:", response.status, errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      const botMessage = this.createChatBotMessage(data.response);
      
      this.setState((prev) => ({
        ...prev,
        messages: [...prev.messages, botMessage],
      }));
    } catch (error) {
      console.error("Full error details:", error);
      const errorMessage = this.createChatBotMessage(`Fout bij ophalen antwoord: ${error.message}`);
      this.setState((prev) => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
      }));
    }
  }
}

export default function Home() {
  return (
    <div style={{ maxWidth: "400px", margin: "auto", padding: "20px" }}>
      <Chatbot 
        config={config} 
        messageParser={MessageParser} 
        actionProvider={ActionProvider} 
        placeholderText="Schrijf hier je bericht"
        headerText="Gesprek met VerhuisBot"
      />
    </div>
  );
}