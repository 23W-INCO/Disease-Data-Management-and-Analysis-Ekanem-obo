// Define dimensions of the chart
const margin = { top: 20, right: 20, bottom: 30, left: 50 },
      width = 960 - margin.left - margin.right,
      height = 500 - margin.top - margin.bottom;

// Define the scales and axes
const x = d3.scaleTime().range([0, width]);
const y = d3.scaleLinear().range([height, 0]);
let xAxis;
const yAxis = d3.axisLeft(y);

// Define the line generator for cholesterol values
const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.cholesterol));

// Create the SVG container for the chart
const svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Tooltip div
const tooltip = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

// Filter variables
let cholesterolFilter = [100, 300];
let bmiFilter = [15, 35];
let groupedData;

// Function to update the chart based on filters
function updateFilteredChart(data) {
  // Apply filters
  const filteredData = data.filter(d => {
    return d.cholesterol >= cholesterolFilter[0] && d.cholesterol <= cholesterolFilter[1] &&
           d.BMI >= bmiFilter[0] && d.BMI <= bmiFilter[1];
  });

  // Call updateChart with filtered data
  updateChart(filteredData);
}

// Function to update the chart
function updateChart(selectedPatientData) {
  // Update the scales
  x.domain(d3.extent(selectedPatientData, d => d.date));
  y.domain([0, d3.max(selectedPatientData, d => d.cholesterol)]);

  // Update the axes
  svg.select(".x.axis").call(xAxis);
  svg.select(".y.axis").call(yAxis);

  // Bind the data to the line
  const patientLine = svg.selectAll(".line")
      .data([selectedPatientData], d => d.date);

  // Enter + update
  patientLine.enter().append("path")
      .attr("class", "line")
      .merge(patientLine)
      .attr("d", line);

  // Exit
  patientLine.exit().remove();

  // Bind the data to the points
  const points = svg.selectAll(".point")
      .data(selectedPatientData, d => d.date);

  // Enter + update
  points.enter().append("circle")
      .attr("class", "point")
      .merge(points)
      .attr("r", 5)
      .attr("cx", d => x(d.date))
      .attr("cy", d => y(d.cholesterol))
      .on("mouseover", (event, d) => {
        tooltip.transition()
          .duration(200)
          .style("opacity", .9);
        tooltip.html(`Date: ${d3.timeFormat("%Y-%m-%d")(d.date)}<br/>Cholesterol: ${d.cholesterol}<br/>BP: ${d.BP}<br/>MED: ${d.Med}<br/>BMI: ${d.BMI}`)
          .style("left", `${event.pageX}px`)
          .style("top", `${event.pageY - 28}px`);
      })
      .on("mouseout", () => {
        tooltip.transition()
          .duration(500)
          .style("opacity", 0);
      });

  // Exit
  points.exit().remove();
}

// Group data by patient name
function groupByPatient(data) {
  return data.reduce((acc, currentValue) => {
    const name = currentValue.name;
    if (!acc[name]) {
      acc[name] = [];
    }
    acc[name].push(currentValue);
    return acc;
  }, {});
}

// Function to load and process the data
function loadData() {
  d3.json("/data").then(data => {
    // Parse dates and cast the cholesterol values
    data.forEach(d => {
      d.date = d3.timeParse("%Y-%m-%d")(d.date);
      d.cholesterol = +d.cholesterol;
    });

    // Determine distinct years
    const years = [...new Set(data.map(d => d.date.getFullYear()))];
    
    // Define the x-axis with unique years as tick values
    xAxis = d3.axisBottom(x)
      .tickValues(years.map(year => new Date(year, 0, 1))) // Sets ticks to the first of each year
      .tickFormat(d3.timeFormat("%Y"));

    // Group the data by patient
    groupedData = groupByPatient(data);

    // Populate the dropdown
    const select = d3.select("#patient-select")
      .on("change", function() {
        updateFilteredChart(groupedData[this.value]);
      });

    select.selectAll("option")
      .data(Object.keys(groupedData))
      .enter().append("option")
        .text(d => d);

    // Initialize the chart with the first patient's data
    const firstPatientName = Object.keys(groupedData)[0];
    updateFilteredChart(groupedData[firstPatientName]);

    // Initialize sliders
    d3.select("#cholesterol-slider")
      .on("input", function() {
        cholesterolFilter[0] = +this.value;
        d3.select("#cholesterol-value").text(this.value);
        updateFilteredChart(groupedData[document.getElementById('patient-select').value]);
      });

    d3.select("#bmi-slider")
      .on("input", function() {
        bmiFilter[0] = +this.value;
        d3.select("#bmi-value").text(this.value);
        updateFilteredChart(groupedData[document.getElementById('patient-select').value]);
      });
  });
}

// Add the X Axis
svg.append("g")
    .attr("transform", `translate(0,${height})`)
    .attr("class", "x axis");

// Add X Axis Label
svg.append("text")             
    .attr("transform", `translate(${width / 2}, ${height + margin.top + 10})`)
    .style("text-anchor", "middle")
    .text("Date");


// Add the Y Axis
svg.append("g")
    .attr("class", "y axis");

// Add Y Axis Label
svg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - margin.left)
    .attr("x", 0 - (height / 2))
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .text("Cholesterol Level");

// Load the data and initialize the chart
loadData();

function downloadChartAsPNG() {
  var svgElement = document.querySelector('#chart svg');
  var serializer = new XMLSerializer();
  var svgString = serializer.serializeToString(svgElement);

  var canvas = document.createElement('canvas');
  canvas.width = width + margin.left + margin.right;
  canvas.height = height + margin.top + margin.bottom;
  canvg(canvas, svgString);  // requires canvg library

  var imgData = canvas.toDataURL('image/png');
  var downloadLink = document.createElement('a');
  downloadLink.href = imgData;
  downloadLink.download = 'lineChart.png';
  document.body.appendChild(downloadLink);
  downloadLink.click();
  document.body.removeChild(downloadLink);
}

document.getElementById('downloadBtn').addEventListener('click', downloadChartAsPNG);
