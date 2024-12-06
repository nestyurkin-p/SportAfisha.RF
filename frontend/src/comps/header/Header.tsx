import { Button, Input } from "@mui/joy";
import "./Header.css";
import FloatingLabelInput from "../controls/FloatingLabelInput";

function AuthModal() {
  return (
    <div
      className="modal fade"
      id="authModal"
      tabindex="-1"
      aria-labelledby="authModalLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h1 className="modal-title fs-5" id="authModalLabel">
              Авторизация
            </h1>
            <button
              type="button"
              className="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div className="modal-body">
            <FloatingLabelInput label="Логин" />
            <FloatingLabelInput
              label="Пароль"
              props={{ type: "password" }}
              className="auth-password-button"
            />
            <Button sx={{ mt: 3 }} className="container">
              Войти
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Header() {
  return (
    <>
      <div className="header prevent-selection bg-body-tertiary d-flex justify-content-between align-items-center shadow-sm">
        <img
          className="head-logo"
          src="/images/head-logo.svg"
          alt="Федерация спортивного программирования России"
        />
        <div className="route-item">
          <img alt="Главная" src="/images/home.svg" />
          <span className="route-label">Главная</span>
        </div>
        <div className="route-item">
          <img
            className="profile-logo-img"
            src="/images/profile.svg"
            alt="Профиль"
          />
          <span
            className="route-label"
            data-bs-toggle="modal"
            data-bs-target="#authModal"
          >
            Профиль
          </span>
        </div>
      </div>
      <AuthModal />
    </>
  );
}
