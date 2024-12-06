import "./EventCalendar.css";
import Button from "@mui/joy/Button";
import Select from "@mui/joy/Select";
import Option from "@mui/joy/Option";
import { ChevronLeft, ChevronRight } from "@mui/icons-material";

function OfficeFilter() {
  return (
    <>
      <Select
        variant="outlined"
        defaultValue="interregional"
        className="office-filter"
      >
        <Option value="interregional">Межрегиональный</Option>
      </Select>
    </>
  );
}

function CalendarHeader() {
  return (
    <>
      <div className="header-content">
        <div className="navigation-controls">
          <Button
            sx={{ mr: 2 }}
            variant="outlined"
            color="neutral"
            className="navigation-button"
          >
            <ChevronLeft />
          </Button>
          <Button
            variant="outlined"
            color="neutral"
            className="navigation-button"
          >
            <ChevronRight />
          </Button>
          <div className="navigation-label">Декабрь 2024</div>
        </div>
        <OfficeFilter />
      </div>
    </>
  );
}

function CalendarGridCell({ day, idx }) {
  return (
    <div key={idx} className="day-cell">
      <span className="date">{day.date}</span>
      {day.events.length > 0 && (
        <div className="events">
          {day.events.map((event, eventIdx) => (
            <div key={eventIdx} className="event" title={event}></div>
          ))}
        </div>
      )}
    </div>
  );
}

function CalendarGrid({ events }) {
  const daysInMonth = 31;
  const month = "Декабрь 2024";
  const firstDay = 0; // Воскресенье (считается индексом первого дня)

  const generateDays = () => {
    const days = [];
    for (let i = 1; i <= daysInMonth; i++) {
      const dayString = i.toString().padStart(2, "0");
      const eventKey = `${dayString}-12-2024`;
      days.push({
        date: i,
        events: events.get(eventKey) || [],
      });
    }
    return days;
  };

  const days = generateDays();

  return (
    <div className="calendar-grid">
      {[
        "Воскресенье",
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
      ].map((day, idx) => (
        <div key={idx} className="day-header">
          {day}
        </div>
      ))}
      {Array(firstDay)
        .fill(null)
        .map((_, idx) => (
          <div key={idx} className="empty-cell" />
        ))}
      {days.map((day, idx) => (
        <CalendarGridCell day={day} idx={idx} />
      ))}
    </div>
  );
}

export default function EventCalendar({ events }) {
  return (
    <>
      <div className="event-calendar">
        <CalendarHeader />
        <CalendarGrid events={events} />
      </div>
    </>
  );
}
