import { scaleLinear } from "d3-scale";
import { interpolateRgb } from "d3-interpolate";

export const getHeatColor = (gradient, minValue, maxValue) => (value) => {
  const colorScale = scaleLinear()
    .domain([minValue, (minValue + maxValue) / 2, maxValue])
    .range(gradient)
    .interpolate(interpolateRgb);
  return colorScale(value);
};

export function darkenColor(color, percentage) {
  // Extract the RGB values
  var rgbValues = color.match(/\d+/g);
  var r = parseInt(rgbValues[0]);
  var g = parseInt(rgbValues[1]);
  var b = parseInt(rgbValues[2]);

  // Calculate the percentage to darken
  var darkenFactor = 1 - percentage;

  // Darken the RGB values
  r = Math.round(r * darkenFactor);
  g = Math.round(g * darkenFactor);
  b = Math.round(b * darkenFactor);

  // Construct the darkened color string
  var darkenedColor = "rgb(" + r + ", " + g + ", " + b + ")";

  return darkenedColor;
}

export function rgbToHex(color) {
  // Extract the RGB values
  var rgbValues = color.match(/\d+/g);
  var r = parseInt(rgbValues[0]);
  var g = parseInt(rgbValues[1]);
  var b = parseInt(rgbValues[2]);

  // Convert the RGB values to hexadecimal
  var hex = "#" + ((r << 16) | (g << 8) | b).toString(16).padStart(6, "0");

  return hex;
}
