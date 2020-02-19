// maze definition
const LINES = [
    [20, 140,260,140],
    [140,140,140,260],
    [260,260,380,260],
    [260,260,260,380],
    [20, 20, 380, 20],
    [20, 20, 20, 380],
    [20, 380,380,380],
    [380, 20,380,380],
];

const rgbToHex = rgb => { 
    let hex = Number(Math.round(rgb)).toString(16);
    if (hex.length < 2) hex = "0" + hex;
    return hex;
};

const fullColorHex = (r,g,b) => "#"+rgbToHex(r)+rgbToHex(g)+rgbToHex(b);


const tintedHex = (r,g,b,p) => fullColorHex(
    r + p*(255-r),
    g + p*(255-g),
    b + p*(255-b)
)

const tintedRgba = (re, gr, bl, p) => 'rgba('+[
    re + (1-p)*(255-re),
    gr + (1-p)*(255-gr),
    bl + (1-p)*(255-bl),
    10*p
].join(',') + ')';

const sqrt2PI = Math.sqrt(Math.PI * 2);
function Gaussian(parameters) {
    this.sigma = parameters.sigma;
    this.mu = parameters.mu;
    this.k = this.mu.length; // dimension
    try {
        var det = numeric.det(this.sigma);
        this._sinv = numeric.inv(this.sigma); // π ^ (-1)
        this._coeff = 1 / (Math.pow(sqrt2PI, this.k) * Math.sqrt(det));
        if ( !(isFinite(det) && det > 0 && isFinite(this._sinv[0][0]))) {
            throw new Error("Invalid matrix");
        }
    } catch(e) {
        this._sinv = numeric.rep([this.k, this.k], 0);
        this._coeff = 0;
        console.log(e);
    }
}

Gaussian.prototype.density = function(x) {
    var delta = numeric.sub(x, this.mu); // 𝛿 = x - mu
    // Compute  Π = 𝛿T . Σ^(-1) . 𝛿
    var P = 0;
    for(var i=0; i<this.k; i++) {
        var sinv_line = this._sinv[i];
        var sum = 0;
        for(var j=0; j<this.k; j++) {
            sum += sinv_line[j] * delta[j];
        }
        P += delta[i] * sum
    }

    // Return: e^(-Π/2) / √|2.π.Σ|
    return this._coeff * Math.exp(P / -2);
};


function get_illustration(id, width=400, height=200) {
    const canvas = document.getElementById(id);
    const ctx = canvas.getContext("2d");
    const pixelRatio = window.devicePixelRatio || 1;
    canvas.width = pixelRatio*width;
    canvas.height = pixelRatio*height;
    ctx.scale(pixelRatio, pixelRatio);
    ctx.mozImageSmoothingEnabled = false;
    ctx.imageSmoothingEnabled = false;
    const rc = rough.canvas(canvas);
    return [ctx, rc];
}

function line_intersection(l1, l2) {
    // returns false if no intersection, otherwise point of intersection

    const s1_x = l1[2] - l1[0];
    const s1_y = l1[3] - l1[1];
    const s2_x = l2[2] - l2[0];
    const s2_y = l2[3] - l2[1];
  
    const s = (-s1_y * (l1[0] - l2[0]) + s1_x * (l1[1] - l2[1])) / (-s2_x * s1_y + s1_x * s2_y);
    const t = ( s2_x * (l1[1] - l2[1]) - s2_y * (l1[0] - l2[0])) / (-s2_x * s1_y + s1_x * s2_y);
  
    if (s >= 0 && s <= 1 && t >= 0 && t <= 1) {
        return [l1[0] + (t * s1_x), l1[1] + (t * s1_y)];
    }
    
    return false;
}


function make_maze(canvas_id, robots, numbers=true) {
    const [ctx, rc] = get_illustration(canvas_id, width=400, height=400);

    ctx.font = '60px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = "grey";
    
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

    if (numbers) {
        numloop: for (let i=0; i<9; i++) {
            for (let r=0; r<robots.length; r++) {
                if (robots[r].pos == i) continue numloop;
            }

            ctx.fillText(i,
                80+120*(i%3),
                70+120*Math.floor(i/3)+30
            );
        }
    }
    
    for (let line of LINES) rc.line(...line);
    
    const sline = { roughness: 1.5, stroke: 'red', strokeWidth:0.5 };

    // robots
    for (let r=0; r<robots.length; r++) {
        let i = robots[r].pos;
        let x = 80+120*(i%3)
        let y = 80+120*Math.floor(i/3);
        
        rc.circle(
            x, y, 48, {roughness:0.5, fill:robots[r].color}
        );
        
        // compute sensor line length:
        let angles = [
            robots[r].angle-5,
            robots[r].angle,
            robots[r].angle+5
        ]
        
        for (let i=0; i<3; i++) {
            const a = (angles[i]-90) * Math.PI / 180;
            
            const beam = [
                x + 30*Math.cos(a),
                y + 30*Math.sin(a),
                x + 500*Math.cos(a),
                y + 500*Math.sin(a)
            ];
            
            let min_s = 1000;
            for (line of LINES) {
                intersection = line_intersection(beam, line);
                                
                if (intersection == false) continue;
                
                let s = Math.sqrt(
                    Math.pow(beam[0] - intersection[0],2) +
                    Math.pow(beam[1] - intersection[1],2)
                )
                
                if (s < min_s) min_s = s;
            }
            
            min_s -= 10;
            rc.line(
                beam[0],
                beam[1],
                beam[0] + min_s*Math.cos(a),
                beam[1] + min_s*Math.sin(a),
                sline
            );
        }
    }
}