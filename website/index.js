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


function make_maze(canvas_id, robots) {
    const [ctx, rc] = get_illustration(canvas_id, width=400, height=400);

    ctx.font = '60px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = "grey";
    
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

    numloop: for (let i=0; i<9; i++) {
        for (let r=0; r<robots.length; r++) {
            if (robots[r].pos == i) continue numloop;
        }

        ctx.fillText(i,
            80+120*(i%3),
            70+120*Math.floor(i/3)+30
        );
    }

    // maze
    const lines = [
        [20, 140,260,140],
        [140,140,140,260],
        [260,260,380,260],
        [260,260,260,380],
        [20, 20, 380, 20],
        [20, 20, 20, 380],
        [20, 380,380,380],
        [380, 20,380,380],
        
    ];
    
    for (let line of lines) {
        rc.line(...line);
    }
    
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
            for (line of lines) {
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