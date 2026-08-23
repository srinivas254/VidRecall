import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HomePage } from "./homePage";
import { ProcessVideo } from "./processVideo";
import { StartSession } from "./startSession";
import { ChatSession } from "./chatSession";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={ <HomePage /> }/>
        <Route path="/process" element={ <ProcessVideo />} />
        <Route path="/session" element={ <StartSession />} />
        <Route path="/chat" element={ <ChatSession />} />
      </Routes>

      <ToastContainer position="top-right" />
    </BrowserRouter>
  );
}
