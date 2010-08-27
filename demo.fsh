uniform float time;

varying vec4 p;

float width = 800.0;
float height = 450.0;
float aspect = width / height;

vec3 sphere_center = vec3(0.0, 0.0, -3.0);
float sphere_radius = 1.5;

vec3 light = vec3(2.0, 2.0, 0.0);

float spherefunc(vec3 p) {
	return length(p - sphere_center) - sphere_radius;
}

vec3 spherenormal(vec3 p) {
	return normalize(p - sphere_center);
}

float twospherefunc(vec3 p) {
	vec3 sphere_center2 = vec3(sphere_center.x-1.0, sphere_center.y, sphere_center.z);
	float d1 = length(p - sphere_center) - sphere_radius;
	float d2 = length(p - sphere_center2) - sphere_radius;
	return min(d1, d2);
}

float spikedsphere(vec3 p) {
	float spikeheight = sin(time)*0.2;
	float spikefreq = 20.0;
	float d1 = length(p - sphere_center) - sphere_radius;
	vec3 diff = normalize(p - sphere_center);
	float offx = spikeheight*sin(spikefreq*diff.x+time);
	float offy = spikeheight*sin(spikefreq*diff.y+time);
	return d1 + offx + offy;
}

float blubsphere(vec3 p) {
	float sphere_radius = 1.0;
	float dist = length(p - sphere_center) - sphere_radius;
	float off = 1.0*sin(2.0*p.y+time);
	return dist + off;
}

float manyspherefunc(vec3 q) {
	return spherefunc(vec3(mod(q.x,2.0), q.y, -mod(-q.z, 4.0)));
}

vec3 colpos = vec3(0.0,0.0,-3.0);
float columnfunc(vec3 p) {
	return max(abs(p.x-colpos.x) - 1.0, abs(p.z-colpos.z) - 1.0);
}

vec3 columnnormal(vec3 p) {
	vec3 d = p - colpos;
	if(abs(d.x) < abs(d.z)) {
		return vec3(0.0,0.0,1.0)*sign(d.z);
	} else {
		return vec3(1.0,0.0,0.0)*sign(d.x);
	}
}

float colspherefunc(vec3 p) {
	float d1 = columnfunc(p);
	float d2 = spherefunc(p);
	if((d1 < 0.3) && (d2 < 0.3)) {
		float s = smoothstep(0.0, 1.0, length(p));
		return mix(d1, d2, s);
	} else {
		return min(d1,d2);
	}
}

void main()
{
	mat4 m_cam = mat4(2.0 * aspect / width, 0.0,          0.0, 0.0,
                      0.0,         2.0 / height, 0.0, 0.0,
                      0.0,         0.0,          0.0, 0.0,
                     -1.0 * aspect,        -1.0,         -1.0, 1.0);

	vec4 ray = m_cam * gl_FragCoord;
	ray = normalize(ray);

	vec3 ray_s = vec3(ray);
	float stepwidth = 0.1;
	float maxdepth = 3.0;
	int n_steps = int(maxdepth / stepwidth);
	vec3 ray_inc = ray_s * stepwidth;

	float s = 1.0, min_step = 0.05;
	int i = 0, imax = 30;
	while( (s > min_step) && (i < imax) ){
		s = spikedsphere(ray_s);
		ray_s += vec3(ray.xyz) * s;
		i++;
	}

	if(s <= min_step) {
		vec3 normal = spherenormal(ray_s);
		vec3 lightdir = normalize(light - ray_s);
		float diffuse = dot(normal, lightdir);
		gl_FragColor = vec4(diffuse,diffuse,diffuse,1.0);
		return;
	}

	float z = -ray.z;
	gl_FragColor = vec4(z,z,z,1.0);
}
