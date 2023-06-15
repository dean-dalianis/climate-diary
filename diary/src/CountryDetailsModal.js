import Modal from "react-modal";
import React from "react";

export function CountryDetailsModal(props) {
  return <Modal
      isOpen={props.open}
      onRequestClose={props.onRequestClose}
      contentLabel="Country Information"
  >
    <h2>Country Information</h2>
    {props.selectedCountry ? (
        <div>
          <p>Country Name: {props.selectedCountry.countryName}</p>
          <p>Average Temperature: {props.selectedCountry.total / props.selectedCountry.count}</p>
          <p>Number of Data Points: {props.selectedCountry.count}</p>
        </div>
    ) : (
        <p>No data available for this country.</p>
    )}
    <button onClick={props.onRequestClose}>Close</button>
  </Modal>;
}