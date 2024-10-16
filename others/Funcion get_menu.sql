-- FUNCTION: public.get_menu(integer, character varying)
-- DROP FUNCTION IF EXISTS public.get_menu(integer, character varying);

CREATE OR REPLACE FUNCTION public.get_menu(
	id_cliente integer,
	id_usuario character varying)
    RETURNS json
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$

DECLARE 
	MSJE JSON :='[]';
	PRODUCT RECORD;
	TPO_NODO TEXT;
	PATH TEXT;
BEGIN
	FOR PRODUCT IN select md.id_modulo, md.desc_modulo, md.nod_lft, md.nod_rgt, md.path_modulo 
	from usr_prf up, perfiles_modulo pm, modulos md 
	where id_usr = id_usuario
		and pm.id_prf = up.id_prf
		and md.id_modulo = pm.id_modulo
		and md.id_clt = id_cliente
		order by md.id_modulo asc
 	LOOP
		IF PRODUCT.NOD_RGT - PRODUCT.NOD_LFT = 1 THEN
			TPO_NODO := 'HIJO';
		ELSE
			TPO_NODO := 'PADRE';
		END IF;
		MSJE := MSJE::jsonb || jsonb_build_object(
			'id_modulo', PRODUCT.id_modulo,
			'tpo_nodo',TPO_NODO,
			'descripcion',PRODUCT.desc_modulo,
			'path',PRODUCT.path_modulo
		)::jsonb;
	
	END LOOP;
	RETURN MSJE;
	END;
	
$BODY$;

ALTER FUNCTION public.get_menu(integer, character varying)
    OWNER TO "AdminAura";
