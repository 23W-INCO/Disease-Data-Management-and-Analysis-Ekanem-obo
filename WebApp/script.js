async function fetchData() {
    const response = await fetch('http://127.0.0.1:5000/data');
    const data = await response.json();
    createLineChart(data.slice(0, 10));
}

function createLineChart(patientData) {
    // Set the dimensions and margins of the graph
    const margin = { top: 50, right: 30, bottom: 30, left: 60 },
          width = 460 - margin.left - margin.right,
          height = 400 - margin.top - margin.bottom;

    // Append the svg object to the chart div
    const svg = d3.select("#chart")
      .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Add X axis
    const x = d3.scaleLinear()
      .domain([0, patientData.length - 1])
      .range([0, width]);
    svg.append("g")
      .attr("transform", `translate(0, ${height})`)
      .call(d3.axisBottom(x));

    // Add Y axis
    const y = d3.scaleLinear()
      .domain([0, d3.max(patientData, d => d.BMI)])
      .range([height, 0]);
    svg.append("g")
      .call(d3.axisLeft(y));

    // Add X axis label
    svg.append("text")
      .attr("text-anchor", "end")
      .attr("x", width)
      .attr("y", height + margin.top + 20)
      .text("Patient Index");

    // Add Y axis label
    svg.append("text")
      .attr("text-anchor", "end")
      .attr("transform", "rotate(-90)")
      .attr("y", -margin.left + 20)
      .attr("x", -margin.top)
      .text("BMI");

    // Add chart title
    svg.append("text")
      .attr("x", (width / 2))             
      .attr("y", 0 - (margin.top / 2))
      .attr("text-anchor", "middle")  
      .style("font-size", "16px") 
      .style("text-decoration", "underline")  
      .text("BMI of Patients");

    // Tooltip Div
    const tooltip = d3.select("#chart")
      .append("div")
      .style("opacity", 0)
      .attr("class", "tooltip")
      .style("background-color", "white")
      .style("border", "solid")
      .style("border-width", "1px")
      .style("border-radius", "5px")
      .style("padding", "10px")
      .style("position", "absolute");

    // Add the line
    svg.append("path")
      .datum(patientData)
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 1.5)
      .attr("d", d3.line()
          .x((d, i) => x(i))
          .y(d => y(d.BMI))
      );

    // Create dots for each data point
    svg.selectAll(".dot")
      .data(patientData)
      .enter().append("circle")
        .attr("class", "dot")
        .attr("cx", (d, i) => x(i))
        .attr("cy", d => y(d.BMI))
        .attr("r", 5)
        .on("mouseover", function(event, d) {
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html("Patient: " + d.name + "<br/>BMI: " + d.BMI)
                .style("left", (event.pageX) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function(d) {
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });
}

fetchData();
