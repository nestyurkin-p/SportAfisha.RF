import "./Header.css";

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
          <span className="route-label">Профиль</span>
        </div>
      </div>
    </>
  );
}
