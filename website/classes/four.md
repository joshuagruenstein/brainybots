# Particle Party

<raw>
<canvas class="illustration" id="discrete" style="height:400px"></canvas>
<p class="caption">A rendering of our current state belief representation.</p>
<script>
(function() {

make_maze("discrete", [], numbers=false);
const rc = rough.canvas(document.getElementById("discrete"));

for (let i=80; i<=320; i+=120) for (let j=80; j<=320; j+=120) {
    rc.circle(
        i, j, Math.pow(Math.random()*7,2), 
        {roughness:5, fill:"green",stroke:"green", fillStyle:"cross-hatch"}
    );
}
})();
</script>
</raw>

<raw>
<canvas class="illustration" id="gaussian" style="height:400px"></canvas>
<p class="caption">A 2D gaussian state belief representation.</p>
<script>
(function() {
make_maze("gaussian", [], numbers=false);
const rc = rough.canvas(document.getElementById("gaussian"));

const g = new Gaussian({mu:[180,180], sigma:[[5000, 2500], [2500, 5000]]});
const grain = 10;

const max = g.density(g.mu);
const min = Math.min(
    g.density([0,0]),
    g.density([360,0]),
    g.density([0,360]),
    g.density([360,360])
);

for (let x=20 + grain/2; x<380; x+=grain) {
    for (let y=20 + grain/2; y<380; y+=grain) {
        const p = (g.density([x-20,y-20])-min)/(max-min);
                
        rc.rectangle(x-grain/2,y-grain/2,grain,grain, {
            roughness:2,
            fill:tintedRgba(0,128,0,p),
            stroke:"none",
            fillStyle:"cross-hatch",
        });

    }
}
})();
</script>
</raw>

<raw>
<canvas class="illustration" id="particle" style="height:400px"></canvas>
<p class="caption">A particle state belief representation.</p>
<script>
(function() {
make_maze("particle", [], numbers=false);
const rc = rough.canvas(document.getElementById("particle"));

const v = 50;
const centers = [
    [20+60,20+60],
    [20+60,20+60+120],
    [20+60+240,20+60+240]
];

for (let [x,y] of centers) {
    for (let i=0; i<5+Math.floor(Math.random()*5); i++) {
        rc.circle(
            x + v*(0.5-Math.random()),
            y + v*(0.5-Math.random()), 5+10*Math.random(),
            { stroke:"green" }
        )
    }
}
})();
</script>
</raw>