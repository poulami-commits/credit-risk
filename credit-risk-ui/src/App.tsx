import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard  from "./pages/Dashboard";
import Assessment from "./pages/Assessment";
import Health     from "./pages/Health";
import ModelInfo  from "./pages/ModelInfo";
import Sidebar    from "./components/Sidebar";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <div className="layout">
        <Sidebar />
        <div className="content">
          <Routes>
            <Route path="/"           element={<Dashboard />}  />
            <Route path="/assessment" element={<Assessment />} />
            <Route path="/health"     element={<Health />}     />
            <Route path="/model-info" element={<ModelInfo />}  />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
