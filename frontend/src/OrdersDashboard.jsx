import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import bg from "./assets/bg.jpg";

const API_URL = "http://localhost:5000";

export default function OrdersDashboard() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  const [userId, setUserId] = useState("");
  const [total, setTotal] = useState("");
  const [itemsText, setItemsText] = useState(
    JSON.stringify([{ product_id: "p1", qty: 2 }], null, 2)
  );

  const navigate = useNavigate();

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/orders`);
      const data = await res.json();
      setOrders(data.orders || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const markAsPaid = async (id) => {
    try {
      await fetch(`${API_URL}/api/orders/${id}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "paid" }),
      });
      fetchOrders();
    } catch (e) {
      console.error(e);
    }
  };

  const createOrder = async (e) => {
    e.preventDefault();
    try {
      const items = JSON.parse(itemsText);
      await fetch(`${API_URL}/api/orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId.trim(),
          items,
          total: Number(total),
        }),
      });
      setUserId("");
      setTotal("");
      fetchOrders();
    } catch (e) {
      alert("Items JSON inválido. Revisa el campo Items.");
      console.error(e);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("auth");
    navigate("/");
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const stats = useMemo(() => {
    const totalOrders = orders.length;
    const paid = orders.filter((o) => o.status === "paid").length;
    const pending = orders.filter((o) => o.status !== "paid").length;
    const totalValue = orders.reduce((sum, o) => sum + (Number(o.total) || 0), 0);
    return { totalOrders, paid, pending, totalValue };
  }, [orders]);

  return (
    <div className="min-h-screen text-white">
      {/* Background con overlay negro */}
      <div
        className="fixed inset-0 -z-10 bg-cover bg-center"
        style={{ backgroundImage: `url(${bg})` }}
      />
      <div className="fixed inset-0 -z-10 bg-black/85 backdrop-blur-[2px]" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 sm:py-10">
        {/* Header mejorado con gradiente azul */}
        <div className="flex flex-col gap-4 sm:gap-6 md:flex-row md:items-center md:justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <span className="text-3xl sm:text-4xl">🛒</span>
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-500">
                  Microservices Orders
                </span>
              </h1>
            </div>
            <p className="mt-2 text-base sm:text-lg md:text-xl text-slate-300">
              API Gateway: <span className="font-semibold text-blue-400">{API_URL}</span>
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            <button
              onClick={fetchOrders}
              className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 px-6 py-3 text-base sm:text-lg font-semibold active:scale-[0.99] transition border border-blue-400/30 shadow-lg shadow-blue-500/20"
            >
              🔄 Refresh
            </button>
            
            <button
              onClick={handleLogout}
              className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600 px-6 py-3 text-base sm:text-lg font-semibold active:scale-[0.99] transition border border-red-400/30 shadow-lg shadow-red-500/20"
            >
              🚪 Logout
            </button>
          </div>
        </div>

        {/* Stats Cards mejoradas con azul */}
        <div className="mt-6 sm:mt-8 grid grid-cols-2 gap-3 sm:gap-5 lg:grid-cols-4">
          <StatCard title="Total Orders" value={stats.totalOrders} icon="📦" color="blue" />
          <StatCard title="Paid" value={stats.paid} icon="✅" color="emerald" />
          <StatCard title="Pending" value={stats.pending} icon="⏳" color="amber" />
          <StatCard title="Total Value" value={`$${stats.totalValue.toLocaleString()}`} icon="💰" color="cyan" />
        </div>

        {/* Main Content Grid */}
        <div className="mt-6 sm:mt-8 grid grid-cols-1 gap-4 sm:gap-6 lg:grid-cols-5">
          {/* Create Order Form - Mejorado */}
          <div className="lg:col-span-2 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 p-4 sm:p-6 shadow-2xl">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                Create Order
              </h2>
              <span className="rounded-lg bg-blue-500/20 px-3 py-1 text-xs sm:text-sm font-semibold border border-blue-400/30 text-blue-300">
                POST /api/orders
              </span>
            </div>

            <form onSubmit={createOrder} className="mt-4 sm:mt-6 space-y-4 sm:space-y-5">
              <div>
                <label className="text-base sm:text-lg font-semibold text-slate-100">
                  User ID
                </label>
                <input
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  placeholder="e.g. 123"
                  className="mt-2 w-full rounded-xl bg-slate-900/80 border border-blue-400/30 px-4 py-2.5 sm:py-3 text-base sm:text-lg outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-blue-400 transition-all"
                  required
                />
              </div>

              <div>
                <label className="text-base sm:text-lg font-semibold text-slate-100">
                  Total
                </label>
                <input
                  value={total}
                  onChange={(e) => setTotal(e.target.value)}
                  placeholder="e.g. 100"
                  className="mt-2 w-full rounded-xl bg-slate-900/80 border border-blue-400/30 px-4 py-2.5 sm:py-3 text-base sm:text-lg outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-blue-400 transition-all"
                  required
                />
              </div>

              <div>
                <label className="text-base sm:text-lg font-semibold text-slate-100">
                  Items (JSON)
                </label>
                <textarea
                  value={itemsText}
                  onChange={(e) => setItemsText(e.target.value)}
                  rows={6}
                  className="mt-2 w-full rounded-xl bg-slate-900/80 border border-blue-400/30 px-4 py-2.5 sm:py-3 text-sm sm:text-base font-mono outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-blue-400 transition-all"
                />
              </div>

              <button
                type="submit"
                className="w-full rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 px-6 py-3 sm:py-4 text-lg sm:text-xl font-extrabold active:scale-[0.99] transition shadow-lg shadow-blue-500/30 transform hover:scale-[1.02]"
              >
                ➕ Create Order
              </button>
            </form>
          </div>

          {/* Orders Table - Mejorado y Responsive */}
          <div className="lg:col-span-3 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 p-4 sm:p-6 shadow-2xl">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4 sm:mb-6">
              <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                Orders List
              </h2>
              <span className="rounded-lg bg-blue-500/20 px-3 py-1 text-xs sm:text-sm font-semibold border border-blue-400/30 text-blue-300">
                GET /api/orders
              </span>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
                <p className="ml-4 text-lg md:text-xl text-slate-200">Loading orders...</p>
              </div>
            ) : orders.length === 0 ? (
              <div className="text-center py-12">
                <span className="text-6xl">📦</span>
                <p className="mt-4 text-lg md:text-xl text-slate-200">
                  No orders yet. Create one! 👈
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto -mx-4 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="min-w-full text-left">
                    <thead className="text-sm sm:text-base md:text-lg text-slate-200 border-b-2 border-blue-400/30">
                      <tr>
                        <th className="py-3 px-2 sm:px-4">ID</th>
                        <th className="py-3 px-2 sm:px-4">User</th>
                        <th className="py-3 px-2 sm:px-4">Total</th>
                        <th className="py-3 px-2 sm:px-4">Status</th>
                        <th className="py-3 px-2 sm:px-4">Action</th>
                      </tr>
                    </thead>

                    <tbody className="text-sm sm:text-base md:text-lg">
                      {orders.map((o) => (
                        <tr
                          key={o._id}
                          className="border-b border-white/10 hover:bg-blue-500/10 transition-colors"
                        >
                          <td className="py-3 sm:py-4 px-2 sm:px-4 font-mono text-xs sm:text-sm text-blue-300">
                            {o._id.slice(-8)}
                          </td>
                          <td className="py-3 sm:py-4 px-2 sm:px-4 font-semibold text-slate-100">
                            {o.user_id}
                          </td>
                          <td className="py-3 sm:py-4 px-2 sm:px-4 font-semibold text-cyan-300">
                            ${Number(o.total).toLocaleString()}
                          </td>
                          <td className="py-3 sm:py-4 px-2 sm:px-4">
                            <StatusPill status={o.status} />
                          </td>
                          <td className="py-3 sm:py-4 px-2 sm:px-4">
                            {o.status !== "paid" ? (
                              <button
                                onClick={() => markAsPaid(o._id)}
                                className="rounded-lg sm:rounded-xl bg-emerald-500 hover:bg-emerald-400 px-3 sm:px-5 py-2 sm:py-3 text-sm sm:text-base font-bold active:scale-[0.99] transition shadow-lg shadow-emerald-500/20"
                              >
                                <span className="hidden sm:inline">✅ Mark as Paid</span>
                                <span className="sm:hidden">✅</span>
                              </button>
                            ) : (
                              <span className="text-slate-400">—</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="mt-4 sm:mt-6 p-3 sm:p-4 rounded-xl bg-blue-500/10 border border-blue-400/30">
              <p className="text-xs sm:text-sm text-blue-200">
                💡 <span className="font-semibold">Tip:</span> Future features: Filter by user_id, search functionality, and pagination.
              </p>
            </div>
          </div>
        </div>

        {/* Footer mejorado */}
        <footer className="mt-8 sm:mt-10 text-center space-y-2">
          <p className="text-sm sm:text-base text-slate-400">
            Built with <span className="text-red-400">❤️</span> using React + Vite + Tailwind CSS
          </p>
          <p className="text-xs sm:text-sm text-slate-500">
            Microservices Architecture Demo • Desarrollado por{" "}
            <span className="text-blue-400 font-semibold">Alejandro De Mendoza</span>
          </p>
        </footer>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }) {
  const colorClasses = {
    blue: "from-blue-500/20 to-cyan-500/20 border-blue-400/30",
    emerald: "from-emerald-500/20 to-green-500/20 border-emerald-400/30",
    amber: "from-amber-500/20 to-yellow-500/20 border-amber-400/30",
    cyan: "from-cyan-500/20 to-blue-500/20 border-cyan-400/30",
  };

  return (
    <div className={`rounded-2xl bg-gradient-to-br ${colorClasses[color]} backdrop-blur-md border p-4 sm:p-5 shadow-xl hover:scale-[1.02] transition-transform`}>
      <div className="flex items-center justify-between">
        <p className="text-xs sm:text-sm md:text-base text-slate-300 font-medium">{title}</p>
        <span className="text-xl sm:text-2xl">{icon}</span>
      </div>
      <p className="mt-2 text-2xl sm:text-3xl md:text-4xl font-extrabold text-white">{value}</p>
    </div>
  );
}

function StatusPill({ status }) {
  const isPaid = status === "paid";
  return (
    <span
      className={[
        "inline-flex items-center rounded-full px-2 sm:px-4 py-1 sm:py-2 text-xs sm:text-sm md:text-base font-bold border whitespace-nowrap",
        isPaid
          ? "bg-emerald-500/20 text-emerald-300 border-emerald-400/40"
          : "bg-amber-500/20 text-amber-300 border-amber-400/40",
      ].join(" ")}
    >
      {status}
    </span>
  );
}