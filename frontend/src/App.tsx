import { CssVarsProvider, extendTheme } from "@mui/joy/styles";
import Header from "./comps/header/Header";
import EventCalendar from "./comps/calendar/EventCalendar";
import ApplicationList from "./comps/application/ApplicationList";
import ApplicationEdit from "./comps/application/ApplicationEdit";
import RegionList from "./comps/region/RegionList";
import UserEdit from "./comps/profile/UserEdit";
import OfficeEdit from "./comps/profile/OfficeEdit";

const applications = [
  {
    name: "Заявка 1",
    status: "Принято",
    comment: "Продуктовая разработка",
  },
  { name: "Заявка 2", status: "В работе", comment: "-" },
  { name: "Заявка 3", status: "Отклонено", comment: "Недостаточно информации" },
];

// Change mui JoyUI to use JetBrains Mono fonts
const theme = extendTheme({
  fontFamily: {
    body: "JetBrains Mono",
  },
});

export default function App() {
  return (
    <>
      <CssVarsProvider theme={theme}>
        <div className="container-fluid">
          <div className="row">
            <Header />
          </div>
          <div className="row my-4 px-4">
            <EventCalendar />
            {/* <ApplicationList applications={applications} /> */}
            {/* <RegionList /> */}
            {/* <UserEdit /> */}
            {/* <OfficeEdit /> */}
          </div>
        </div>
      </CssVarsProvider>
    </>
  );
}
