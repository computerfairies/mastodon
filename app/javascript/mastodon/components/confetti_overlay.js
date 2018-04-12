import React from 'react';

// ✨ magic constants ✨
const FRICTION = 2e-2;
const GRAVITY = 8;
const RAIN_PROBABILITY = 5;
const CANNON_PROBABILITY = 0.8;
const CANNON_MIN = 10;
const CANNON_MAX = 50;

const MAX_PARTICLES = 64;
const MIN_PARTICLES = 8;

const PARTICLE_DELETE_PROBABILITY = 1;

// note: months start at 0 in javascript because, fuck if i know
const BIRTHDAY = new Date(Date.UTC(2017, 3, 12, 0, 0));
const BIRTHDAY_TOLERANCE = 24*60*60*1000;

function is_birthday(date){
  date = new Date(date);
  const birthday = new Date(BIRTHDAY);
  birthday.setUTCFullYear(date.getUTCFullYear());
  return +date > +birthday && +date < +birthday + BIRTHDAY_TOLERANCE;
  // the weird use of unary + is to cast the dates to numbers
}

function clamp(n, bot, top){
  return Math.min(top, Math.max(bot, n));
}

function brandom(bot, top){
  // bounded random
  // the args are labeled bot and top but they can be reversed
  return Math.random() * (top - bot) + bot
}

function crandom(a){
  // centered random. it's centered around zero
  return brandom(-a, a);
}

class Particle {
  constructor(){
    this.hue = 0;
    this.mass = 1;
    this.x = 0;
    this.y = 0;
    this.vx = 0;
    this.vy = 0;
    this.dead = true;
    this.flutter_speed = 4;
    this.luminosity = 50;
  }

  throw(x, y, vx, vy){
    this.hue = Math.floor(Math.random()*360);
    this.mass = 1 + crandom(.2);
    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.flutter_speed = 4 * crandom(4);
    this.dead = false;
  }

  update(t, dt){
    this.vx = this.vx / (1 + FRICTION*dt*Math.abs(this.vx));
    this.vy = (this.vy + GRAVITY) / (1 + FRICTION*dt*Math.abs(this.vy));

    this.x = this.x + this.vx * dt * this.mass;
    this.y = this.y + this.vy * dt * this.mass;
    // yes I am aware that adding mass here doesn't make
    // physical sense but whatever it looks more interesting

    this.luminosity = 60 + Math.sin(t*this.flutter_speed)**3 * 30;
  }

  draw(ctx){
    ctx.fillStyle = `hsl(${this.hue}, 100%, ${this.luminosity}%)`;
    ctx.fillRect(this.x - 1, this.y - 1, 2, 2);
  }
}

export default class ConfettiOverlay extends React.Component {
  constructor(props) {
    super(props);

    this.canvas = null;
    this.setCanvas = c => {
      this.canvas = c
      if(c){
        this.ctx = c.getContext('2d');
      } else {
        this.ctx = null;
      }
    };

    this.halted = true;
    this.started = false;

    this.frame = this.frame.bind(this);
  }

  should_show() {
    return (
      this.props.status.get('content').match(/🎉|🎊/) &&
      is_birthday(this.props.status.get('created_at'))
    );
  }

  componentDidMount(){
    if(this.should_show()){
      this.setup();
      this.start();
    }
  }

  componentWillUnmount(){
    this.stop();
  }

  componentDidUpdate(prevProps, prevState){
    if(this.status !== prevProps.status){
      if(this.should_show()){
        this.setup()
        if(!this.started){
          this.start()
        }
      } else {
        this.stop();
      }
    }
  }

  render() {
    if(this.should_show()){
      return <canvas ref={this.setCanvas} className='confetti-overlay' />;
    }
    return null;
  }

  make_it_rain(){
    let particle;
    for(const candidate of this.particles){
      if(candidate.dead){
        particle = candidate;
        break;
      }
    }
    if(particle){
      particle.throw(
        Math.random() * this.canvas.width,
        -10,
        crandom(10),
        crandom(10));
    }
  }

  shoot_cannon(){
    let loaded_in_cannon = new Array();
    const cannon_size = brandom(CANNON_MIN, CANNON_MAX)
    for(const candidate of this.particles){
      if(candidate.dead){
        loaded_in_cannon.push(candidate);
        if(loaded_in_cannon.length >= cannon_size){
          break;
        }
      }
    }
    const from_left = Math.random() > 0.5;
    const x_sign = from_left? 1 : -1;
    const x = from_left? 0 : this.canvas.width;
    const y = brandom(this.canvas.height/4, this.canvas.height);
    const angle = Math.PI / 4 + crandom(Math.PI / 8);


    for(const particle of loaded_in_cannon){
      const particle_angle = brandom(angle, Math.PI/2);
      const speed = 1000 + crandom(600);
      particle.throw(
        x + x_sign * brandom(-15, 0),
        y + crandom(30),
        x_sign * Math.cos(particle_angle) * speed,
        - Math.sin(particle_angle) * speed
      )
    }
  }

  on_intersect(entries){
    for(const entry of entries){
      if(entry.target == this.container){
        if(this.halted && entry.isIntersecting){
          requestAnimationFrame(this.frame);
          this.halted = !this.halted;
        } else if(!this.halted && !entry.isIntersecting) {
          this.halted = !this.halted;
        }
      }
    }
  }

  maybe_resize(){
    const container_bounds = this.container.getBoundingClientRect();

    const container_height = Math.ceil(container_bounds.height);
    const container_width = Math.ceil(container_bounds.width);

    if(this.canvas.width !== container_width ||
      this.canvas.height !== container_height){
      this.canvas.width = container_width;
      this.canvas.height = container_height;
    }
  }

  frame(t){
    // standard housekeeping
    let dt = t - this.last_frame;
    this.last_frame = t;

    if(this.halted){
      return;
    }

    requestAnimationFrame(this.frame);

    // t and dt are in milliseconds.
    // for convenience let's convert them to seconds
    t = t/1e3;
    dt = dt/1e3;
    // and clamp dt.. dont want no wayward confetti because someones
    // computer froze for ten seconds
    dt = clamp(dt, 0, 0.05);

    this.maybe_resize();

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    if(Math.random() / RAIN_PROBABILITY < dt){
      this.make_it_rain();
    }

    if(Math.random() / CANNON_PROBABILITY < dt){
      this.shoot_cannon();
    }

    for(const particle of this.particles){
      if(!particle.dead){
        particle.update(t, dt);
        particle.draw(this.ctx);
        if(particle.y > this.canvas.height * 1.1){
          particle.dead = true;
        }
      }
    }

    // delete particles over time
    if((Math.random() / PARTICLE_DELETE_PROBABILITY < dt
      // delete a particle if we drop a frame
        || dt > 0.017)
        && this.particles.length > MIN_PARTICLES){
      this.particles.pop();
    }
  }

  setup() {
    this.container = this.canvas.parentElement;
    this.maybe_resize();

    this.particles = new Array();
    for(let i = 0; i < MAX_PARTICLES; i++){
      const particle = new Particle();
      this.particles.push(particle);
      if(i < RAIN_PROBABILITY*2){
        particle.throw(
          Math.random() * this.canvas.width,
          Math.random() * this.canvas.height,
          0,
          150
        )
      }
    }
  }

  start() {
    if(window.IntersectionObserver){
      this.intersection_observer =
        new IntersectionObserver(this.on_intersect.bind(this));
      this.intersection_observer.observe(this.container);
    } else {
      requestAnimationFrame(this.frame);
    }
    this.last_frame = performance.now();
    this.started = true;
  }

  stop() {
    this.halted = true;
    this.started = false;
    this.particles = null;
    if(this.intersection_observer){
      this.intersection_observer.disconnect();
    }
  }
}
