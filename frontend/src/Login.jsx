import { useState } from "react";
import { useNavigate } from "react-router-dom";
import logo from './assets/logo.png';

export default function Login() {
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();

    // CREDENCIALES DEMO
    if (user === "admin" && pass === "admin") {
      localStorage.setItem("auth", "true");
      navigate("/dashboard");
    } else {
      alert("Credenciales incorrectas");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white relative px-4 py-8">
      {/* Imagen de logo de fondo con efecto de sombra y centrado */}
      <div className="absolute inset-0 flex justify-center items-center overflow-hidden">
        <img
          src={logo}
          alt="Logo"
          className="max-w-full max-h-[70vh] object-contain opacity-50 shadow-xl"
        />
      </div>

      {/* Título de la página - MEJORADO CON AZUL Y RESPONSIVE */}
      <h1 className="absolute top-4 md:top-10 px-4 text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-extrabold text-center w-full z-10">
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-sky-500">
          Bienvenido al Dashboard de Arquitectura de Microservicios
        </span>
        <br />
        <span className="text-white text-xl sm:text-2xl md:text-3xl lg:text-4xl mt-2 inline-block">
          Sistema de Gestión de Pedidos
        </span>
      </h1>

      {/* Formulario de login - MEJORADO Y RESPONSIVE */}
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-[90%] sm:max-w-md md:max-w-lg bg-white/10 backdrop-blur-md border border-white/20 p-6 sm:p-8 md:p-10 rounded-2xl shadow-2xl relative z-10 mt-32 sm:mt-40 md:mt-48"
      >
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-center mb-6 sm:mb-8 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
          🔐 Login
        </h1>

        <div className="mb-4 sm:mb-5">
          <label className="block mb-2 font-semibold text-sm sm:text-base">
            Usuario
          </label>
          <input
            value={user}
            onChange={(e) => setUser(e.target.value)}
            className="w-full rounded-xl bg-slate-900/80 border border-white/20 px-4 py-3 sm:py-3.5 outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-400/30 transition-all text-sm sm:text-base"
            placeholder="admin"
            required
          />
        </div>

        <div className="mb-6 sm:mb-8">
          <label className="block mb-2 font-semibold text-sm sm:text-base">
            Contraseña
          </label>
          <input
            type="password"
            value={pass}
            onChange={(e) => setPass(e.target.value)}
            className="w-full rounded-xl bg-slate-900/80 border border-white/20 px-4 py-3 sm:py-3.5 outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-400/30 transition-all text-sm sm:text-base"
            placeholder="admin"
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 transition-all duration-300 rounded-xl py-3 sm:py-4 text-lg sm:text-xl font-extrabold shadow-lg hover:shadow-blue-500/50 transform hover:scale-[1.02]"
        >
          Entrar
        </button>

        <p className="mt-4 sm:mt-6 text-center text-slate-300 text-xs sm:text-sm">
          Usuario: <b className="text-blue-400">admin</b> · Contraseña: <b className="text-blue-400">admin</b>
        </p>
      </form>

      {/* Footer con autor */}
      <div className="absolute bottom-4 w-full text-center text-slate-400 text-xs sm:text-sm z-10 px-4">
        <p>Desarrollado por <span className="text-blue-400 font-semibold">Alejandro De Mendoza</span></p>
        <p className="mt-1">Ingeniero Informático · Especialista en IA</p>
      </div>
    </div>
  );
}