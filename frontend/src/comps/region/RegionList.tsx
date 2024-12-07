import { Button } from "@mui/joy";
import "./RegionList.css";

function SubjectRow({ subject }: { subject: object }) {
  return (
    <>
      <div className="row">
        <div className="col">{subject.name}</div>
        <div className="col">{subject.agent}</div>
        <div className="col">{subject.contacts}</div>
      </div>
    </>
  );
}

function RegionInfo({ region }: { region: object }) {
  return (
    <>
      <div className="row subject-heading">
        <div className="col">Субъект РФ</div>
        <div className="col">Представитель</div>
        <div className="col">Контакты</div>
      </div>
      {region.subjects.map((subject: object, idx: number) => (
        <SubjectRow subject={subject} />
      ))}
    </>
  );
}

function Moscow() {
  return (
    <div className="text-center">
      <RegionInfo
        region={{
          name: "г. Москва",
          subjects: [
            {
              name: "г. Москва",
              agent: "Анашкин Евгений Юрьевич",
              contacts: "fspmsk@mail.ru",
            },
          ],
        }}
      />
    </div>
  );
}

function RegionRow({ region, idx }: { region: any; idx: number }) {
  const collapseId = `event${idx}`;
  return (
    <>
      <button
        className="row btn border shadow-sm m-2 py-3 d-flex"
        style={{ fontSize: "10pt" }}
        data-bs-toggle="collapse"
        data-bs-target={"#" + collapseId}
        aria-expanded="false"
        aria-controls={"#" + collapseId}
      >
        {region.name}
        <div className="collapse pt-2" id={collapseId}>
          <RegionInfo region={region} />
        </div>
      </button>
    </>
  );
}

function RegionListItems({ regions = [] }) {
  return (
    <>
      <div className="d-flex flex-column">
        {regions.map((region: object, idx: number) => (
          <RegionRow region={region} idx={idx} />
        ))}
      </div>
    </>
  );
}

function RegionCreateButton() {
  return (
    <>
      <Button
        sx={{ bgcolor: "#4561FD", mt: 3, width: "25%" }}
        className="align-self-end"
      >
        Добавить федеральный округ
      </Button>
    </>
  );
}

const regions = [
  {
    name: "Центральный федеральный округ",
    subjects: [
      {
        name: "Брянская область",
        agent: "Казаков Олег Дмитриевич",
        contacts: "bryansk@fsp-russia.com",
      },
      {
        name: "Брянская область",
        agent: "Казаков Олег Дмитриевич",
        contacts: "bryansk@fsp-russia.com",
      },
      {
        name: "Брянская область",
        agent: "Казаков Олег Дмитриевич",
        contacts: "bryansk@fsp-russia.com",
      },
      {
        name: "Брянская область",
        agent: "Казаков Олег Дмитриевич",
        contacts: "bryansk@fsp-russia.com",
      },
    ],
  },
  {
    name: "Центральный федеральный округ",
    subjects: [
      {
        name: "Брянская область",
        agent: "Казаков Олег Дмитриевич",
        contacts: "bryansk@fsp-russia.com",
      },
    ],
  },
  {
    name: "Центральный федеральный округ",
    subjects: [
      {
        name: "Брянская область",
        agent: "Казаков Олег Дмитриевич",
        contacts: "bryansk@fsp-russia.com",
      },
    ],
  },
];

export default function RegionList() {
  return (
    <>
      <div className="px-5">
        <div className="border shadow-sm p-3 d-flex flex-column">
          <Moscow />
          <RegionListItems regions={regions} />
          <RegionCreateButton />
        </div>
      </div>
    </>
  );
}
