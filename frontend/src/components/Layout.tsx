import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Upload, Settings, BarChart3, Menu } from 'lucide-react';
import clsx from 'clsx';

const Layout = () => {
    return (
        <div className="flex h-screen bg-gray-50">
            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-md flex-shrink-0">
                <div className="p-6 border-b">
                    <h1 className="text-xl font-bold text-blue-600 flex items-center gap-2">
                        <LayoutDashboard className="w-6 h-6" />
                        CopyKAT
                    </h1>
                    <p className="text-xs text-gray-500 mt-1">CNV Analysis Pipeline</p>
                </div>
                <nav className="p-4 space-y-2">
                    <NavLink
                        to="/"
                        className={({ isActive }) => clsx(
                            "flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                            isActive ? "bg-blue-50 text-blue-700" : "text-gray-700 hover:bg-gray-100"
                        )}
                    >
                        <Upload className="w-4 h-4" />
                        Upload Data
                    </NavLink>
                    <NavLink
                        to="/configure"
                        className={({ isActive }) => clsx(
                            "flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                            isActive ? "bg-blue-50 text-blue-700" : "text-gray-700 hover:bg-gray-100"
                        )}
                    >
                        <Settings className="w-4 h-4" />
                        Configure
                    </NavLink>
                    <NavLink
                        to="/results"
                        className={({ isActive }) => clsx(
                            "flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                            isActive ? "bg-blue-50 text-blue-700" : "text-gray-700 hover:bg-gray-100"
                        )}
                    >
                        <BarChart3 className="w-4 h-4" />
                        Results
                    </NavLink>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto p-8">
                <div className="max-w-7xl mx-auto">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default Layout;

