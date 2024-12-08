import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router";
import "./index.css";
import App from "./App.tsx";
import ApplicationList from "./comps/application/ApplicationList.tsx";
import { useAtom, useAtomValue } from "jotai";
import EventCalendar from "./comps/calendar/EventCalendar.tsx";
import roleAtom from "./atoms";
import UserEdit from "./comps/profile/UserEdit.tsx";

function Panel() {
  const role = useAtom(roleAtom);
  return (
    <>
      {role === "superuser" || role === "office" ? (
        <ApplicationList />
      ) : (
        <UserEdit />
      )}
    </>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<App />}>
          <Route index element={<EventCalendar />} />
          <Route path="panel" element={<Panel />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);
