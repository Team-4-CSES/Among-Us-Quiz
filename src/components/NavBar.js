import React from "react";
import "../style/navbar.css";
import styled from 'styled-components'

import Links from "./Links";

const Container = styled.div.attrs({
  className: "container-fluid { padding: 0;}",
})``;

const Nav = styled.nav.attrs({
  className: "navbar navbar-expand-lg navbar-dark bg-dark",
})`
  margin-bottom: 20 px;
`;

const NavBar = (props) => {
  return (
    <Container>
      <Nav>
        <Links />
      </Nav>
    </Container>
  );
};

export default NavBar;
