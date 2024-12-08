import { Button, Input } from "@mui/joy";
import "./Header.css";
import FloatingLabelInput from "../controls/FloatingLabelInput";
import { useState } from "react";
import { useNavigate } from "react-router";
import { useAtom } from "jotai";
import accessToken from "../../atoms";

function AuthModal() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("markmelix@gmail.com");
  const [password, setPassword] = useState("toor");
  const [token, setToken] = useAtom(accessTokenAtom);
  const [role, setRole] = useAtom(roleAtom);

  const login = () => {
    navigate("/panel");
    setToken("");
    setRole("superuser");
  };

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
            <FloatingLabelInput
              label="Логин"
              props={{ onChange: (e) => setUsername(e.target.value) }}
            />
            <FloatingLabelInput
              label="Пароль"
              props={{ type: "password" }}
              className="auth-password-button"
              props={{ onChange: (e) => setPassword(e.target.value) }}
            />
            <Button sx={{ mt: 3 }} className="container" onClick={login}>
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
