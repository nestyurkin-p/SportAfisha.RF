import "./App.css";

function Header() {
  return (
    <>
      <div className="header bg-body-tertiary d-flex justify-content-between align-items-center container-fluid shadow-sm">
        <div className="head-logo prevent-selection">
          <img
            src="./public/images/head-logo.svg"
            alt="Федерация спортивного программирования России"
          />
        </div>
      </div>
    </>
  );
}

function App() {
  return (
    <>
      <Header />
    </>
  );
}

export default App;
