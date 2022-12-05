/**
 * Test of an optimization of https://adventofcode.com/2022/day/5 made by pengi
 *
 * It is written to try an optimization where all operations is caluclated in
 * reverse order, so no data needs to be moved, but just track the location of
 * the final 9 top crates.
 *
 * It doesn't matter, and might even be slightly slower, on the normal input
 * files. But for test files crafted with about 1 million crates in each stack
 * it should be siginificantly faster
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct d5_stack
{
    char *storage;
    int len;
    int size;
};

struct d5_op
{
    int count;
    int from;
    int to;
};

struct d5_op_stack
{
    struct d5_op *ops;
    int len;
    int size;
};

struct d5_context
{
    struct d5_stack *stack[9];
    struct d5_op_stack *ops;
};

struct d5_crate
{
    int stack;
    int loc;
};

struct d5_stack *
stack_alloc(void)
{
    struct d5_stack *stack;
    stack = malloc(sizeof(struct d5_stack));
    stack->len = 0;
    stack->size = 65536;
    stack->storage = malloc(stack->size);
}

void stack_append(struct d5_stack *stack, char c)
{
    if (stack->len >= stack->size)
    {
        stack->size *= 2;
        stack->storage = realloc(stack->storage, stack->size);
    }
    stack->storage[stack->len++] = c;
}

struct d5_op_stack *opstack_alloc(void)
{
    int i;
    struct d5_op_stack *ops = malloc(sizeof(struct d5_op_stack));
    ops->len = 0;
    ops->size = 65536;
    ops->ops = malloc(sizeof(struct d5_op) * ops->size);
    return ops;
}

void opstack_append(struct d5_op_stack *ops, int count, int from, int to)
{
    if (ops->len >= ops->size)
    {
        ops->size *= 2;
        ops->ops = realloc(ops->ops, sizeof(struct d5_op) * ops->size);
    }
    ops->ops[ops->len].count = count;
    ops->ops[ops->len].from = from;
    ops->ops[ops->len].to = to;
    ops->len++;
}

void crate_process_part1(struct d5_crate *crate, struct d5_op *op)
{
    if (crate->stack == op->to)
    {
        if (crate->loc >= op->count)
        {
            /* Remain, but move in stack */
            crate->loc -= op->count;
        }
        else
        {
            /* Moved */
            crate->stack = op->from;
            crate->loc = op->count - crate->loc - 1;
        }
    }
    else if (crate->stack == op->from)
    {
        /* Remain, but move in stack */
        crate->loc += op->count;
    }
}

void crate_process_part2(struct d5_crate *crate, struct d5_op *op)
{
    if (crate->stack == op->to)
    {
        if (crate->loc >= op->count)
        {
            /* Remain, but move in stack */
            crate->loc -= op->count;
        }
        else
        {
            /* Moved */
            crate->stack = op->from;
        }
    }
    else if (crate->stack == op->from)
    {
        /* Remain, but move in stack */
        crate->loc += op->count;
    }
}

struct d5_context *ctx_alloc(void)
{
    int i;
    struct d5_context *ctx = malloc(sizeof(struct d5_context));
    for (i = 0; i < 9; i++)
    {
        ctx->stack[i] = stack_alloc();
    }
    ctx->ops = opstack_alloc();
    return ctx;
}

struct d5_context *parse(FILE *fp)
{
    char linebuf[128];
    int i;
    struct d5_context *ctx = ctx_alloc();

    /* Parse stacks */
    do
    {
        if (NULL == fgets(linebuf, 128, fp))
        {
            fprintf(stderr, "unexpected end of input while reading stacks\n");
            return ctx;
        }
        /* Add stack variables */
        for (i = 0; i < 9; i++)
        {
            if (linebuf[i * 4] == '[')
            {
                stack_append(ctx->stack[i], linebuf[i * 4 + 1]);
            }
        }
    } while (linebuf[1] != '1');

    /* For printability */
    for (i = 0; i < 9; i++)
    {
        stack_append(ctx->stack[i], '\0');
        ctx->stack[i]->len--;
    }

    /* linebuf contains number line, read empty line */
    if (NULL == fgets(linebuf, 128, fp))
    {
        return ctx;
    }
    if (linebuf[0] != '\n')
    {
        fprintf(stderr, "expected empty line\n");
        return ctx;
    }

    /* Parse ops */
    while (fgets(linebuf, 128, fp))
    {
        char *saveptr;
        char *tok;
        int count, from, to;
        /* "move" = */ strtok_r(linebuf, " \n", &saveptr);
        count = atoi(strtok_r(NULL, " \n", &saveptr));
        /* "from" = */ strtok_r(NULL, " \n", &saveptr);
        from = atoi(strtok_r(NULL, " \n", &saveptr)) - 1;
        /* "to" = */ strtok_r(NULL, " \n", &saveptr);
        to = atoi(strtok_r(NULL, " \n", &saveptr)) - 1;
        opstack_append(ctx->ops, count, from, to);
    }

    return ctx;
}

int main(int argc, char *argv[])
{
    int i, it;
    struct d5_context *ctx;
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s <input file>\n", argv[0]);
        return -1;
    }

    ctx = parse(fopen(argv[1], "r"));
    for (i = 0; i < 9; i++)
    {
        printf("Stack %d: %d/%d\n", i + 1, ctx->stack[i]->len, ctx->stack[i]->size);
    }
    printf("Ops %d/%d\n", ctx->ops->len, ctx->ops->size);

    struct d5_crate creates[9];

    /* Part 1 */
    for (i = 0; i < 9; i++)
    {
        creates[i].loc = 0;
        creates[i].stack = i;
    }

    for (it = ctx->ops->len - 1; it >= 0; it--)
    {
        struct d5_op *op = &ctx->ops->ops[it];
        for (i = 0; i < 9; i++)
        {
            crate_process_part1(&creates[i], op);
        }
    }

    printf("Part 1: ");
    for (i = 0; i < 9; i++)
    {
        printf("%c", ctx->stack[creates[i].stack]->storage[creates[i].loc]);
    }
    printf("\n");

    /* Part 2 */
    for (i = 0; i < 9; i++)
    {
        creates[i].loc = 0;
        creates[i].stack = i;
    }

    for (it = ctx->ops->len - 1; it >= 0; it--)
    {
        struct d5_op *op = &ctx->ops->ops[it];
        for (i = 0; i < 9; i++)
        {
            crate_process_part2(&creates[i], op);
        }
    }

    printf("Part 2: ");
    for (i = 0; i < 9; i++)
    {
        printf("%c", ctx->stack[creates[i].stack]->storage[creates[i].loc]);
    }
    printf("\n");

    return 0;
}