import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./Login";
import OrdersDashboard from "./OrdersDashboard";

function RequireAuth({ children }) {
  const isAuth = localStorage.getItem("auth") === "true";
  return isAuth ? children : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <Router>
      <Routes>
        {/* LOGIN */}
        <Route path="/" element={<Login />} />

        {/* DASHBOARD PROTEGIDO */}
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <OrdersDashboard />
            </RequireAuth>
          }
        />

        {/* CUALQUIER OTRA RUTA */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
