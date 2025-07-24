import { Outlet } from "react-router-dom"
import Form from "./components/Form"
import Home from "./components/Home"

function App() {

  return (
    <>
    {/* <Home /> */}
    <Outlet />
    </>
  )
}

export default App
