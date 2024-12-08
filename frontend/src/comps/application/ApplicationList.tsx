import { Button } from "@mui/joy";
import { useNavigate } from "react-router";

function ApplicationListHeader() {
  return (
    <div className="row text-center mx-2 my-3" style={{ fontSize: "12pt" }}>
      <div className="col">Название заявки</div>
      <div className="col">Статус</div>
      <div className="col">Комментарий</div>
    </div>
  );
}

function ApplicationRow({ application }: { application: any }) {
  const nagivate = useNavigate();
  return (
    <>
      <button
        className="row btn border shadow-sm m-2 py-3 d-flex"
        style={{ fontSize: "10pt" }}
        onClick={() => navigate(`/application/${application.id}`)}
      >
        <div className="col">{application.name}</div>
        <div className="col">{application.status}</div>
        <div className="col">{application.comment}</div>
      </button>
    </>
  );
}

function ApplicationListItems({ applications = [] }) {
  return (
    <>
      <div className="d-flex flex-column">
        {applications.map((app: object, idx: number) => (
          <ApplicationRow application={app} />
        ))}
      </div>
    </>
  );
}

function ApplicationCreateButton() {
  return (
    <>
      <Button
        sx={{ bgcolor: "#4561FD", mt: 3, width: "20%" }}
        className="align-self-end"
      >
        Создать новую заявку
      </Button>
    </>
  );
}

export default function ApplicationList() {
  const applications = [
    {
      id: "app1",
      name: "Заявка 1",
      status: "Принято",
      comment: "Продуктовая разработка",
    },
    {
      id: "app2",
      name: "Заявка 2",
      status: "В работе",
      comment: "-",
    },
    {
      id: "app3",
      name: "Заявка 3",
      status: "Отклонено",
      comment: "Недостаточно информации",
    },
  ];

  return (
    <>
      <div className="px-5">
        <div className="border shadow-sm p-3 d-flex flex-column">
          <ApplicationListHeader />
          <ApplicationListItems applications={applications} />
          <ApplicationCreateButton />
        </div>
      </div>
    </>
  );
}
