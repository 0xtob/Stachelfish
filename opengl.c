#include <GL/glew.h>

#include <GL/gl.h>

#define NO_SDL_GLEXT
#include <SDL/SDL.h>

//#include <stdio.h>
//#include <stdlib.h>

#include "demo.vsh.h"
#include "demo.fsh.h"

#undef WITH_GL_ERROR

#ifdef WITH_GL_ERROR
#define CHECK_GL() { \
	GLenum err = glGetError();   \
	while (err != GL_NO_ERROR) { \
            fprintf(stderr, "glError: %s caught at %s:%u\n", (char *)gluErrorString(err), __FILE__, __LINE__); \
            err = glGetError(); \
	} \
}
#else
#define CHECK_GL()
#endif

GLuint p;
GLuint tex;

inline void setTextures()
{
    unsigned char data[512];
    int i;
    for (i=0; i<512; ++i) {
        data[i] = (unsigned char)((random() / (float)RAND_MAX) * 255);
    }
    glGenTextures(1, &tex);
    CHECK_GL();
    glActiveTexture(GL_TEXTURE0);
    CHECK_GL();
    glBindTexture(GL_TEXTURE_1D, tex);
    CHECK_GL();
    //glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    CHECK_GL();
    glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    CHECK_GL();
    glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_NEAREST); 
    CHECK_GL();
    glTexImage1D(GL_TEXTURE_1D, 0, GL_INTENSITY8UI_EXT, 512, 0, GL_LUMINANCE_INTEGER_EXT, GL_UNSIGNED_BYTE, data);
    CHECK_GL();
}

void setShaders() 
{
    
    GLuint v = glCreateShader(GL_VERTEX_SHADER);
    CHECK_GL();
    GLuint f = glCreateShader(GL_FRAGMENT_SHADER);	
    CHECK_GL();
    
    glShaderSource(v, 1, &vertexShader, NULL);
    CHECK_GL();
    glShaderSource(f, 1, &fragmentShader, NULL);
    CHECK_GL();
    
    glCompileShader(v);
    CHECK_GL();
    glCompileShader(f);
    CHECK_GL();
    
    p = glCreateProgram();
    CHECK_GL();
    
    glAttachShader(p,v);
    CHECK_GL();
    glAttachShader(p,f);
    CHECK_GL();
    
    glLinkProgram(p);
    CHECK_GL();
    glUseProgram(p);
    CHECK_GL();
}

int main(int argc, char **argv)
//void _start()
{
//    if( SDL_Init( SDL_INIT_VIDEO ) != 0 )
//    {
//        printf("failed to init SDL.\n");
//        return 1;
//    }
    SDL_Init( SDL_INIT_VIDEO );

    //printf("success.\n");
    
    SDL_GL_SetAttribute( SDL_GL_DOUBLEBUFFER, 1 );
    SDL_SetVideoMode( 800, 450, 32, SDL_OPENGL | SDL_FULLSCREEN);
    SDL_ShowCursor(0);

    glewInit();

    //if (GLEW_OK != err)
    //{
    //    fprintf(stderr, "Error: %s\n", glewGetErrorString(err));
    //    return 1;
    //}

    //glDisable(GL_DEPTH_TEST);

    setShaders();
    setTextures();
    GLint my_time = glGetUniformLocation(p, "t");
    CHECK_GL();
    GLint my_tex = glGetUniformLocation(p, "p");
    CHECK_GL();
    glUniform1i(my_tex, 0);

    Uint32 ticks = 0;
    while (ticks < 1000*60)
    {
        SDL_Event event;

        while( SDL_PollEvent(&event) )
        {
            switch(event.type)
            {
            case SDL_KEYDOWN:
            case SDL_QUIT:
                SDL_Quit();
                exit(0);
                break;
            default:
                break;
            }
        }

        ticks = SDL_GetTicks();
        glUniform1f(my_time, ticks>>10);
        CHECK_GL();
        glRecti(-1, -1, 1, 1);
        CHECK_GL();

        SDL_GL_SwapBuffers();
    }

    SDL_Quit();
    
    return 0;
}
