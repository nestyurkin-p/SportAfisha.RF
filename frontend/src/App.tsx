import Header from "./comps/header/Header";
import EventCalendar from "./comps/event_calendar/EventCalendar";

const events = new Map([
  ["03-12-2024", ["Событие 1", "Событие 2"]],
  ["09-12-2024", ["Событие 3"]],
  ["23-12-2024", ["Событие 4", "Событие 5"]],
  ["25-12-2024", ["Чемпионат и Первенство России"]],
]);

export default function App() {
  return (
    <>
      <div className="container-fluid">
        <div className="row">
          <Header />
        </div>
        <div className="row my-4 px-4">
          <EventCalendar events={events} />
        </div>
      </div>
    </>
  );
}
