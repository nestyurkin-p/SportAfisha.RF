import Header from "./comps/header/Header";
import EventCalendar from "./comps/event_calendar/EventCalendar";
import ApplicationList from "./comps/application/ApplicationList";

const calendarEvents = new Map([
  ["03-12-2024", ["Событие 1", "Событие 2"]],
  ["09-12-2024", ["Событие 3"]],
  ["23-12-2024", ["Событие 4", "Событие 5"]],
  ["25-12-2024", ["Чемпионат и Первенство России"]],
]);

const applications = [
  {
    name: "Заявка 1",
    status: "Принято",
    comment: "Продуктовая разработка",
  },
  { name: "Заявка 2", status: "В работе", comment: "-" },
  { name: "Заявка 3", status: "Отклонено", comment: "Недостаточно информации" },
];

export default function App() {
  return (
    <>
      <div className="container-fluid">
        <div className="row">
          <Header />
        </div>
        <div className="row my-4 px-4">
          {/* <EventCalendar events={calendarEvents} /> */}
          <ApplicationList applications={applications} />
        </div>
      </div>
    </>
  );
}
