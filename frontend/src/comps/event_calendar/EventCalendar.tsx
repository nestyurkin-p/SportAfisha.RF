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
            sx={{ m: 2 }}
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
export default function EventCalendar() {
  return (
    <>
      <CalendarHeader />
    </>
  );
}
