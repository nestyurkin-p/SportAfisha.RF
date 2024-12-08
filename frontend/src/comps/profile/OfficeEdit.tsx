import { Button, Option, Select } from "@mui/joy";
import FloatingLabelInput from "../controls/FloatingLabelInput";

const inputHeight = "56px";

function PersonalEditForm() {
  return (
    <div className="border shadow-sm p-3">
      <h2 className="fs-6 mb-3">Информация о представителе</h2>
      <FloatingLabelInput label="ФИО" minHeight={inputHeight} />
      <Select defaultValue="male" className="mt-3" sx={{ height: inputHeight }}>
        <Option value="male">Мужчина</Option>
        <Option value="female">Женщина</Option>
      </Select>
      <FloatingLabelInput
        label="Дата рождения"
        minHeight={inputHeight}
        props={{ type: "date" }}
        className="mt-3"
      />
    </div>
  );
}

function LocationEditForm() {
  return (
    <div className="border shadow-sm p-3">
      <h2 className="fs-6 mb-3">Регион представительства</h2>
      <FloatingLabelInput label="Федеральный округ" minHeight={inputHeight} />
      <FloatingLabelInput
        className="mt-3"
        label="Регион"
        minHeight={inputHeight}
      />
    </div>
  );
}

function MiscEditForm() {
  return (
    <div className="border shadow-sm p-3">
      <h2 className="fs-6 mb-3">Другие данные</h2>
      <FloatingLabelInput label="Почта" minHeight={inputHeight} />
      <FloatingLabelInput
        className="mt-3"
        label="Номер телефона"
        minHeight={inputHeight}
      />
    </div>
  );
}

function SecurityEditForm() {
  return (
    <div className="border shadow-sm p-3">
      <h2 className="fs-6 mb-3">Безопасность</h2>
      <FloatingLabelInput
        label="Текущий пароль"
        minHeight={inputHeight}
        props={{ type: "password" }}
      />
      <FloatingLabelInput
        className="mt-3"
        label="Новый пароль"
        minHeight={inputHeight}
        props={{ type: "password" }}
      />
      <FloatingLabelInput
        className="mt-3"
        label="Повторите новый пароль"
        minHeight={inputHeight}
        props={{ type: "password" }}
      />
    </div>
  );
}
export default function OfficeEdit() {
  return (
    <>
      <div style={{ padding: "0 10%" }}>
        <div className="row">
          <div className="col">
            <PersonalEditForm />
          </div>
          <div className="col">
            <SecurityEditForm />
          </div>
        </div>
        <div className="row mt-4">
          <div className="col">
            <MiscEditForm />
          </div>
          <div className="col">
            <LocationEditForm />
          </div>
        </div>
        <div className="row d-flex flex-column align-items-center">
          <Button
            sx={{
              width: "20%",
              height: "40px",
              bgcolor: "#4561FD",
              mt: 3,
            }}
          >
            Сохранить
          </Button>
        </div>
      </div>
    </>
  );
}
