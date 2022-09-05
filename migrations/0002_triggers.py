from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iaas', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("""
            CREATE OR REPLACE FUNCTION ipmi_insert()
                RETURNS TRIGGER AS
            $BODY$
            DECLARE
                ipmi_id integer;
            BEGIN
                -----------------------------------------------------
                -- Ensure that only 1 IPMI is active for each pool --
                -- IP by removing the previous IPMI associated     --
                -- with the pool_ip of the new IPMI being created  --
                -----------------------------------------------------
                SELECT id INTO ipmi_id
                FROM ipmi
                WHERE id != NEW.id AND pool_ip_id = NEW.pool_ip_id
                ORDER BY created DESC
                LIMIT 1;
                IF ipmi_id IS NOT NULL THEN
                    UPDATE ipmi
                    SET removed = NEW.created
                    WHERE id = ipmi_id;
                END IF;
                UPDATE pool_ip
                SET updated = NOW() at time zone 'UTC'
                WHERE id = NEW.pool_ip_id;
                RETURN NEW;
            END;
            $BODY$

            LANGUAGE plpgsql VOLATILE
            COST 100;
        """),

        migrations.RunSQL("""
            CREATE TRIGGER ipmi_insert
            BEFORE INSERT ON ipmi
            FOR EACH ROW EXECUTE PROCEDURE ipmi_insert();
        """),
    ]
