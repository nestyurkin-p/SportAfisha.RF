import "./EventCalendar.css";
import { atom, useAtom, useAtomValue, useSetAtom } from "jotai";
import Button from "@mui/joy/Button";
import Select from "@mui/joy/Select";
import Option from "@mui/joy/Option";
import { ChevronLeft, ChevronRight } from "@mui/icons-material";
import { useState } from "react";
import { atomEffect } from "jotai-effect";
import moment from "moment";

const triggerRerenderAtom = atom();
const currentEventAtom = atom();
const currentMonthAtom = atom(moment());
const currentOfficeAtom = atom("Межрегиональный");
const officesAtom = atom(["Межрегиональный", "Москва"]);
const eventsAtom = atom(
  new Map([
    [
      "Межрегиональный",
      [
        ["03-11-2024", ["Событие 1", "Событие 2"]],
        ["03-12-2024", ["Событие 1", "Событие 2"]],
        ["09-12-2024", ["Событие 3"]],
        ["23-12-2024", ["Событие 4", "Событие 5"]],
        ["25-12-2024", ["Чемпионат и Первенство России"]],
        ["01-01-2025", ["Test"]],
      ],
    ],
  ]),
);

function OfficeFilter() {
  const [currentOffice, setCurrentOffice] = useAtom(currentOfficeAtom);
  const offices = useAtomValue(officesAtom);
  return (
    <>
      <Select
        variant="outlined"
        defaultValue={currentOffice}
        className="office-filter"
        handleChange={(event: any, newValue: any) => {
          setCurrentOffice(newValue);
        }}
      >
        {offices.map((office, _) => (
          <>
            <Option value={office}>{office}</Option>
          </>
        ))}
      </Select>
    </>
  );
}

function CalendarHeader() {
  const [currentMonth, setCurrentMonth] = useAtom(currentMonthAtom);
  const [triggerRerender, setTriggerRerender] = useAtom(triggerRerenderAtom);
  return (
    <>
      <div className="header-content">
        <div className="navigation-controls">
          <Button
            sx={{ mr: 2 }}
            variant="outlined"
            color="neutral"
            className="navigation-button"
            onClick={() => {
              setCurrentMonth(currentMonth.subtract(1, "month"));
              setTriggerRerender(!triggerRerender);
            }}
          >
            <ChevronLeft />
          </Button>
          <Button
            variant="outlined"
            color="neutral"
            className="navigation-button"
            onClick={() => {
              setCurrentMonth(currentMonth.add(1, "month"));
              setTriggerRerender(!triggerRerender);
            }}
          >
            <ChevronRight />
          </Button>
          <div className="navigation-label">
            {
              [
                "Январь",
                "Февраль",
                "Март",
                "Апрель",
                "Май",
                "Июнь",
                "Июль",
                "Август",
                "Сентябрь",
                "Октябрь",
                "Ноябрь",
                "Декабрь",
              ][currentMonth.month()]
            }{" "}
            {currentMonth.year()}
          </div>
        </div>
        <OfficeFilter />
      </div>
    </>
  );
}

function CalendarEventModal() {
  const event = useAtomValue(currentEventAtom);
  return (
    <div
      className="modal fade"
      id="calendarEventInfoModal"
      tabindex="-1"
      aria-labelledby="calendarEventInfoModalLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h1 className="modal-title fs-5" id="calendarEventInfoModalLabel">
              {event}
            </h1>
            <button
              type="button"
              className="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div className="modal-body">...</div>
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              data-bs-dismiss="modal"
            >
              Закрыть
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function CalendarGridCell({ day, idx }: { day: any; idx: number }) {
  const setEvent = useSetAtom(currentEventAtom);
  return (
    <div key={idx} className="day-cell">
      <span className="date">{day.date}</span>
      {day.events.length > 0 && (
        <div className="events">
          {day.events.map((event: string, eventIdx: number) => (
            <div
              key={eventIdx}
              className="event"
              title={"🔵 " + event}
              data-bs-toggle="modal"
              data-bs-target="#calendarEventInfoModal"
              onClick={() => setEvent(event)}
            ></div>
          ))}
        </div>
      )}
    </div>
  );
}

function CalendarGrid() {
  useAtom(triggerRerenderAtom);

  const events = useAtomValue(eventsAtom);
  const currentMonth = useAtomValue(currentMonthAtom);
  const daysInMonth = currentMonth.daysInMonth();
  const firstWeekDay = currentMonth.weekday();

  const generateDays = () => {
    const days = [];
    for (let i = 1; i <= daysInMonth; i++) {
      const dayString = i.toString().padStart(2, "0");
      const monthString = (currentMonth.month() + 1)
        .toString()
        .padStart(2, "0");
      const yearString = currentMonth.year().toString().padStart(2, "0");
      const eventKey = `${dayString}-${monthString}-${yearString}`;
      console.log(eventKey);
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
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
      ].map((day, idx) => (
        <div key={idx} className="day-header">
          {day}
        </div>
      ))}
      {Array(firstWeekDay)
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

export default function EventCalendar() {
  return (
    <>
      <CalendarHeader />
      <CalendarGrid />
      <CalendarEventModal />
    </>
  );
}
