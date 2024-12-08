import { Button, Radio, RadioGroup, Slider } from "@mui/joy";
import FloatingLabelInput from "../controls/FloatingLabelInput";
import { useState } from "react";
import { Send } from "@mui/icons-material";

function EventEdit() {
  const [age, setAge] = useState([0, 100]);

  const handleAgeChange = (event: Event, newAge: number | number[]) => {
    setAge(newAge as number[]);
  };

  return (
    <>
      <div className="row">
        <FloatingLabelInput label="Наименование спортивного мероприятия" />
      </div>
      <div className="row mt-3 column-gap-3">
        <div className="col">
          <div className="row">
            <h3 className="fs-6">Пол</h3>
          </div>
          <div className="row">
            <RadioGroup defaultValue="male" name="radio-buttons-group">
              <Radio
                label="Мужчины"
                value="male"
                color="primary"
                orientation="vertical"
                size="sm"
                variant="plain"
                sx={{ flexDirection: "row-reverse" }}
              />
              <Radio
                label="Женщины"
                value="female"
                color="primary"
                orientation="vertical"
                size="sm"
                variant="plain"
                sx={{ flexDirection: "row-reverse" }}
              />
            </RadioGroup>
          </div>
          <div className="row mt-3">
            <FloatingLabelInput label="Дисциплина" />
          </div>
          <div className="row mt-3">
            <h3 className="fs-6">Место проведения</h3>
            <FloatingLabelInput label="Город" className="mt-1" />
            <FloatingLabelInput label="Регион" className="mt-3" />
            <FloatingLabelInput label="Федеральный округ" className="mt-3" />
          </div>
        </div>
        <div className="col">
          <h3 className="fs-6">Возраст</h3>
          <Slider
            getAriaLabel={() => "Temperature range"}
            value={age}
            onChange={handleAgeChange}
            valueLabelDisplay="auto"
            marks={[
              { value: 0, label: "0" },
              { value: 99, label: "99" },
            ]}
          />
          <div style={{ marginTop: "0.835rem" }}></div>
          <FloatingLabelInput
            label="Дата начала"
            props={{ type: "date" }}
            className="mt-2"
          />
          <FloatingLabelInput
            label="Дата конца"
            props={{ type: "date" }}
            className="mt-3"
          />
          <FloatingLabelInput
            label="Число участников"
            props={{ type: "number" }}
            className="mt-3"
          />
        </div>
        <Button sx={{ bgcolor: "#4561FD", mt: 5 }}>Подтвердить заявку</Button>
      </div>
    </>
  );
}

function Chat() {
  return (
    <>
      <div
        className="border d-flex flex-column justify-content-between p-2 mt-3"
        style={{ height: "70vh" }}
      >
        <div className="border" style={{ opacity: 0 }}></div>
        <FloatingLabelInput
          label="Сообщение"
          props={{ type: "text", placeholder: "Введите сообщение" }}
          endDecorator={<Send />}
        />
      </div>
    </>
  );
}

export default function ApplicationEdit({
  application,
}: {
  application: object;
}) {
  return (
    <>
      <div className="px-5">
        <div className="border shadow-sm p-3 row">
          <div className="col">
            <h2 className="fs-5">О мероприятии</h2>
            <div className="row mt-3">
              <EventEdit />
            </div>
          </div>
          <div className="col">
            <h2 className="fs-5">Чат с региональным представителем</h2>
            <Chat />
          </div>
        </div>
      </div>
    </>
  );
}
