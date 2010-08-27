#include <SDL/SDL.h>
#include <SDL/SDL_opengl.h>

#include <stdio.h>

#include "demo.vsh.h"
#include "demo.fsh.h"

#define WITH_GL_ERROR

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
    
    GLuint p = glCreateProgram();
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
{
    if( SDL_Init( SDL_INIT_VIDEO ) != 0 )
    {
        printf("failed to init SDL.\n");
        return 1;
    }

    printf("success.\n");
    
    SDL_SetVideoMode( 800, 450, 32, SDL_OPENGL | SDL_FULLSCREEN );

    glDisable(GL_DEPTH_TEST);

    setShaders();
    
    while (1)
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

        glRecti(-1, -1, 1, 1);

        SDL_GL_SwapBuffers();
    }

    SDL_Quit();
    
    return 0;
}