// simple fragment shader

// 'time' contains seconds since the program was linked.
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

vec3 twospherefunc(vec3 p) {
	vec3 sphere_center2 = vec3(sphere_center.x-1, sphere_center.y, sphere_center.z);
	float d1 = length(p - sphere_center) - sphere_radius;
	float d2 = length(p - sphere_center2) - sphere_radius;
	return min(d1, d2);
//	return min(d1, d2);
}

vec3 spikedsphere(vec3 p) {
	float spikeheight = sin(time)*0.2;
	float spikefreq = 20.0;
	float d1 = length(p - sphere_center) - sphere_radius;
	vec3 diff = normalize(p - sphere_center);
	float offx = spikeheight*sin(spikefreq*diff.x+time);
	float offy = spikeheight*sin(spikefreq*diff.y+time);
	//float off = 0.2 * sin(p.y * 6.0 + 3*time);
	return d1 + offx + offy;
}

vec3 blubsphere(vec3 p) {
	float sphere_radius = 1.0;
	float dist = length(p - sphere_center) - sphere_radius;
	float off = 1*sin(2*p.y+time);
	return dist + off;
}

float manyspherefunc(vec3 q) {
	return spherefunc(vec3(mod(q.x,2.0), q.y, -mod(-q.z, 4.0)));
	//float d1 = spherefunc(q);
	//float d2 = spherefunc(q+vec3(p.x*3,0.0,0.0));
	//if( (d1 < 0.5) && (d2 < 0.5) ) {
	//return min(d1,d2);
	//} else {
	//	return max(d1, d2);
	//}
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
		float s = smoothstep(0, 1, length(p));
		return mix(d1, d2, s);
	} else {
		return min(d1,d2);
	}
}

void main()
{
	// Matrices are given in column-major order
    // (What you see here is thus transposed.
	mat4 m_cam = mat4(2.0 * aspect / width, 0.0,          0.0, 0.0,
                      0.0,         2.0 / height, 0.0, 0.0,
                      0.0,         0.0,          0.0, 0.0,
                     -1.0 * aspect,        -1.0,         -1.0, 1.0);

	vec4 ray = m_cam * gl_FragCoord;
	//ray.z += 0.1*sin(3.0*ray.y+7.0*p.x);
	//ray.x += 0.1*sin(3.0*ray.y+3.0*p.x);
	ray = normalize(ray);

	vec3 ray_s = vec3(ray);
	float stepwidth = 0.1;
	float maxdepth = 3.0;
	int n_steps = int(maxdepth / stepwidth);
	vec3 ray_inc = ray_s * stepwidth;

	// Raymarching
	float s = 1.0, min_step = 0.05;
	int i = 0, imax = 30;
	while( (s > min_step) && (i < imax) ){
		s = spikedsphere(ray_s);
		// We're s units away, so we can advance by
		// at least s units.
		ray_s += ray * s;
		i++;
	}

	// Debug: Show n steps
	//float c = float(i)/10 ;
	//gl_FragColor = vec4(c,c,c,1.0);
	//return;

	if(s <= min_step) {
		vec3 normal = spherenormal(ray_s);
		//vec3 normal = columnnormal(ray_s);
		vec3 lightdir = normalize(light - ray_s);
		float diffuse = dot(normal, lightdir);
		gl_FragColor = vec4(diffuse,diffuse,diffuse,1.0);
		return;
	}

	/*
	// Straightforward raycasting
	for(int i=0; i < n_steps; i++) {
		if(spherefunc(ray_s) < 0.0) {
			vec3 normal = spherenormal(ray_s);
			float diffuse = dot(normal, normalize(light - ray_s));
			gl_FragColor = vec4(diffuse,diffuse,diffuse,1.0);
			return;
		}
		ray_s += ray_inc;
	}
	*/

	// Background
	float z = -ray.z;
	gl_FragColor = vec4(z,z,z,1.0);
}
