var seismics = [[]];
var t_num = 1001;
var x_num = 101;   
var dt_ms = 1;
var spectrum = [];
var freqs = [];
var filename = "Файл не загружен";
var empty = true;

function reset_seismics(init = false) {
    if (init) {
        seismics = Array(t_num).fill(0).map(() => Array(x_num).fill(0));
    }
    xvl = Array.from({ length: x_num }, (v, i) =>  i);
    tvl = Array.from({ length: t_num }, (v, i) =>  i*dt_ms);     

    var data = [
    {
      z: seismics,
      x: xvl,
      y: tvl,
      type: 'heatmap',
      hoverongaps: false,
    }
    ];             

    var layout = {
        title: {text: filename,  y:0.98, yanchor:'top', font: {weight: 'bold', color: 'rgb(0, 160, 138)'}},
        annotations: [],
        xaxis: {
            ticks: '',
            side: 'top',
            autosize: true,
            title: 'Номер трассы',
            mirror: 'ticks',
            rangeslider: {visible:false},
        },
        yaxis: {
            ticks: '',
            ticksuffix: ' ',
            autorange: 'reversed',    
                   
            autosize: false,
            title: 'Время, мс',
            mirror: 'ticks',
            rangeslider: {visible:false},
        },
        
        dragmode : "drawrect",
        newshape : {
            fillcolor: "rgba(55,95,55,1)",
        },
        width: 700,
        height: 700,
        
    };     

    var config = {
      modeBarButtonsToRemove:['pan2d','select2d','lasso2d','resetScale2d', 'zoom2d', 'zoomin2d', 'zoomout2d', 'autoscale2d'],
      displayModeBar: true,
      showAxisDragHandles : false,
    };

    if (init) {
        
        Plotly.newPlot('heatmapDiv', data, layout,config);
      
        first_time = false;
      }
    else {     
   
      Plotly.react('heatmapDiv', data, layout, config);          
    }  

};


function reset_spectrum(init=false, title="Спектр по всем данным") {
    if (init) {
        freqs = Array.from({ length: t_num }, (v, i) =>  1);
        spectrum = Array.from({ length: t_num }, (v, i) =>  1);
    }

    var data = [{
        x: freqs,
        y: spectrum,
        type: 'scatter',
        mode: 'lines',
      }];      
    
  
    var layout = {
        title: {text: title,  y:0.98, yanchor:'top',font: {weight: 'bold'}},
        xaxis: {
            ticks: '',
            side: 'top',
            title: 'Частота, Гц',
            range: [0, Math.max(freqs)],
        },
        yaxis: {
            title: 'Амплитуда',
            range: [0, Math.max(spectrum)],
        },
        width: 600,
        height: 700,        

    } ;

    var config = {
        modeBarButtonsToRemove:['pan2d','select2d','lasso2d','resetScale2d', 'zoom2d', 'zoomin2d', 'zoomout2d', 'autoscale2d'],
        displayModeBar: true,
        showAxisDragHandles : false,
      };

    if (init) {
        
        Plotly.newPlot('linechartDiv', data, layout,config);
      
        first_time = false;
      }
    else {     
   
      Plotly.react('linechartDiv', data, layout, config);          
    }  
}

reset_seismics(true);
reset_spectrum(true);


var heatmapPlot = document.getElementById('heatmapDiv');
var spectrumPlot = document.getElementById('linechartDiv');

heatmapPlot.on('plotly_relayout', function(data){     
    var shape = data.shapes[data.shapes.length - 1];
    
    if (data.shapes.length > 1) {
      console.log('more than 1')
        update_data = {
            'shapes' : [shape],
        }
        Plotly.relayout(heatmapPlot, update_data)
        
    }  
    if (!empty) {
    update_spectrum_data(shape.x0, shape.y0, shape.x1, shape.y1, `Спектр. Трассы: ${ Math.round(shape.x0)}-${ Math.round(shape.x1)}, время: ${ Math.round(shape.y0*dt_ms)}-${ Math.round(shape.y1*dt_ms)}мс`);    
    }
})

// Получаем ссылки на элементы
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');


uploadBtn.addEventListener('click', () => {  
  fileInput.click();
});

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];

  const formData = new FormData();
  formData.append('file', file);

  fetch('http://127.0.0.1:8000/upload', {
    method: 'POST',
    body: formData
  }) 
  .then(response => response.json())
  .then(data  => {
    //console.log(data)
    seismics = data[0];
    dt_ms = data[1]*1000;
    freqs = data[2];
    spectrum = data[3];
    filename = data[4];
    reset_seismics();
    reset_spectrum();   
    empty = false; 
  })
  .catch(error => {
    console.error('Error uploading file:', error);
  });
});

const demodataBtn = document.getElementById('demodataBtn');
demodataBtn.addEventListener('click', () => {
    fetch('http://127.0.0.1:8000/get_testdata', {
        method: 'GET',       
    }) 
    .then(response => response.json())
    .then(data  => {
        //console.log(data)
        seismics = data[0];
        dt_ms = data[1]*1000;
        freqs = data[2];
        spectrum = data[3];
        filename = "Тестовая сейсмограмма"
        reset_seismics();
        reset_spectrum();
        empty = false;        
    })
    .catch(error => {
        console.error('Error uploading file:', error);
    });
});   

function update_spectrum_data(x0, y0, x1, y1, title="Спектр по всем данным")
{
  fetch('http://127.0.0.1:8000/update_spec', {method: 'POST', body: JSON.stringify([x0, y0, x1, y1]),
  headers: {'Content-Type':'application/json'} })
  .then(response => response.json())
  .then(data => {
  freqs = data[0],
  spectrum = data[1],                                  
  
  reset_spectrum(false, title);                                                                  
  })
.catch(error => console.error('Error:', error));  
};

const resetBtn = document.getElementById('resetBtn');
resetBtn.addEventListener('click', () => {
    max_x = Math.floor(heatmapPlot.layout.xaxis.range[1]);
    max_y = Math.floor(heatmapPlot.layout.yaxis.range[0]);   
    update_spectrum_data(0, 0, max_x, max_y);
    update_data = {
            'shapes' : [],
        }
    Plotly.relayout(heatmapPlot, update_data)
})
