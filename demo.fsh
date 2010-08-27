// simple vertex shader

varying vec4 p;

void main()
{
	gl_Position = gl_Vertex;
	p = gl_ModelViewMatrix[1];
//	gl_Position    = gl_ModelViewProjectionMatrix * gl_Vertex;
//	gl_FrontColor  = gl_Color;
//	gl_TexCoord[0] = gl_MultiTexCoord0;
}
